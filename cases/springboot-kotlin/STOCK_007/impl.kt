package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderStatus
import com.example.order.entity.CancellationLog
import com.example.order.repository.OrderRepository
import com.example.order.repository.ProductRepository
import com.example.order.repository.CancellationLogRepository
import com.example.order.exception.OrderNotFoundException
import com.example.order.exception.InvalidOrderStateException
import com.example.order.exception.ProductNotFoundException
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional
class OrderCancellationService(
    private val orderRepository: OrderRepository,
    private val productRepository: ProductRepository,
    private val cancellationLogRepository: CancellationLogRepository,
    private val paymentService: PaymentService,
    private val emailService: EmailService
) {

    private val logger = LoggerFactory.getLogger(OrderCancellationService::class.java)

    fun cancelOrder(orderId: Long, reason: String?, cancelledBy: String): CancellationResponse {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        if (order.status == OrderStatus.CANCELLED) {
            logger.info("Order $orderId already cancelled")
            return CancellationResponse(
                orderId = order.id,
                status = order.status,
                stockRestored = order.stockRestored,
                isDuplicate = true,
                message = "Order was already cancelled"
            )
        }

        validateCancellationAllowed(order)

        val previousStatus = order.status
        order.status = OrderStatus.CANCELLED
        order.cancelledAt = LocalDateTime.now()

        restoreStock(order)

        val savedOrder = orderRepository.save(order)

        logCancellation(orderId, reason, cancelledBy, true)

        initiateRefund(order)

        notifyCustomer(order, reason)

        logger.info("Order $orderId cancelled successfully. Previous status: $previousStatus")

        return CancellationResponse(
            orderId = savedOrder.id,
            status = savedOrder.status,
            stockRestored = true,
            isDuplicate = false,
            message = "Order cancelled successfully"
        )
    }

    fun forceCancelOrder(orderId: Long, reason: String?, adminUser: String): CancellationResponse {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        if (order.status == OrderStatus.CANCELLED) {
            logger.info("Admin force cancel - Order $orderId already cancelled")
            return CancellationResponse(
                orderId = order.id,
                status = order.status,
                stockRestored = order.stockRestored,
                isDuplicate = true,
                message = "Order was already cancelled"
            )
        }

        logger.warn("Admin $adminUser forcing cancellation of order $orderId in status ${order.status}")

        order.status = OrderStatus.CANCELLED
        order.cancelledAt = LocalDateTime.now()

        restoreStock(order)

        val savedOrder = orderRepository.save(order)

        logCancellation(orderId, "ADMIN FORCE CANCEL: $reason", adminUser, true)

        try {
            initiateRefund(order)
        } catch (e: Exception) {
            logger.error("Failed to initiate refund for force-cancelled order $orderId", e)
        }

        return CancellationResponse(
            orderId = savedOrder.id,
            status = savedOrder.status,
            stockRestored = true,
            isDuplicate = false,
            message = "Order force cancelled by admin"
        )
    }

    private fun validateCancellationAllowed(order: Order) {
        when (order.status) {
            OrderStatus.DELIVERED -> throw InvalidOrderStateException(
                "Cannot cancel delivered order. Please process a return instead."
            )
            OrderStatus.SHIPPED -> logger.warn("Cancelling already shipped order ${order.id}")
            else -> {}
        }
    }

    private fun restoreStock(order: Order) {
        logger.info("Restoring stock for order ${order.id}")

        val productIds = order.items.map { it.productId }
        val products = productRepository.findByIdIn(productIds).associateBy { it.id }

        for (item in order.items) {
            val product = products[item.productId]
                ?: throw ProductNotFoundException("Product not found: ${item.productId}")

            val previousStock = product.stockQuantity
            product.stockQuantity += item.quantity

            logger.debug(
                "Restored stock for product ${product.id}: $previousStock -> ${product.stockQuantity} (+${item.quantity})"
            )
        }

        productRepository.saveAll(products.values)
    }

    private fun logCancellation(orderId: Long, reason: String?, cancelledBy: String, stockRestored: Boolean) {
        val log = CancellationLog(
            orderId = orderId,
            cancellationReason = reason,
            stockRestored = stockRestored,
            cancelledBy = cancelledBy
        )
        cancellationLogRepository.save(log)
    }

    private fun initiateRefund(order: Order) {
        try {
            paymentService.processRefund(order.id, order.totalAmount, order.customerId)
            logger.info("Refund initiated for order ${order.id}")
        } catch (e: Exception) {
            logger.error("Failed to initiate refund for order ${order.id}", e)
            throw e
        }
    }

    private fun notifyCustomer(order: Order, reason: String?) {
        try {
            emailService.sendCancellationEmail(
                orderId = order.id,
                customerId = order.customerId,
                reason = reason
            )
        } catch (e: Exception) {
            logger.error("Failed to send cancellation email for order ${order.id}", e)
        }
    }

    fun getCancellationHistory(orderId: Long): List<CancellationLog> {
        return cancellationLogRepository.findByOrderIdOrderByCreatedAtDesc(orderId)
    }
}

data class CancellationResponse(
    val orderId: Long,
    val status: OrderStatus,
    val stockRestored: Boolean,
    val isDuplicate: Boolean,
    val message: String
)

interface PaymentService {
    fun processRefund(orderId: Long, amount: java.math.BigDecimal, customerId: Long)
}

interface EmailService {
    fun sendCancellationEmail(orderId: Long, customerId: Long, reason: String?)
}
