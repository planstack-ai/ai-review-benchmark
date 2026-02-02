package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderStatus
import com.example.order.entity.Product
import com.example.order.entity.StockAdjustment
import com.example.order.entity.AdjustmentType
import com.example.order.repository.OrderRepository
import com.example.order.repository.ProductRepository
import com.example.order.repository.StockAdjustmentRepository
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
    private val stockAdjustmentRepository: StockAdjustmentRepository,
    private val refundService: RefundService,
    private val notificationService: NotificationService
) {

    private val logger = LoggerFactory.getLogger(OrderCancellationService::class.java)

    fun cancelOrder(orderId: Long, reason: String?): CancellationResult {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        validateCancellationAllowed(order)

        val previousStatus = order.status
        order.status = OrderStatus.CANCELLED
        order.cancelledAt = LocalDateTime.now()

        restoreStockForCancelledOrder(order, reason)

        orderRepository.save(order)

        processRefund(order)

        notificationService.sendCancellationNotification(order.id, order.customerId, reason)

        logger.info("Order ${order.id} cancelled. Previous status: $previousStatus")

        return CancellationResult(
            orderId = order.id,
            previousStatus = previousStatus,
            cancelledAt = order.cancelledAt!!,
            refundInitiated = true,
            stockRestored = true
        )
    }

    fun cancelOrderItem(orderId: Long, itemId: Long, reason: String?): PartialCancellationResult {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        validatePartialCancellationAllowed(order)

        val item = order.items.find { it.id == itemId }
            ?: throw IllegalArgumentException("Order item not found: $itemId")

        restoreSingleItem(item.productId, item.quantity, orderId, reason)

        order.items.remove(item)

        if (order.items.isEmpty()) {
            order.status = OrderStatus.CANCELLED
            order.cancelledAt = LocalDateTime.now()
        } else {
            recalculateOrderTotal(order)
        }

        orderRepository.save(order)

        return PartialCancellationResult(
            orderId = order.id,
            itemId = itemId,
            productId = item.productId,
            quantityRestored = item.quantity,
            orderFullyCancelled = order.items.isEmpty()
        )
    }

    private fun validateCancellationAllowed(order: Order) {
        if (order.status == OrderStatus.CANCELLED) {
            throw InvalidOrderStateException("Order is already cancelled")
        }

        if (order.status == OrderStatus.DELIVERED) {
            throw InvalidOrderStateException("Cannot cancel delivered order. Please process a return instead.")
        }

        if (order.status == OrderStatus.SHIPPED) {
            logger.warn("Cancelling order ${order.id} that is already shipped")
        }
    }

    private fun validatePartialCancellationAllowed(order: Order) {
        if (order.status == OrderStatus.CANCELLED) {
            throw InvalidOrderStateException("Cannot partially cancel already cancelled order")
        }

        if (order.status == OrderStatus.DELIVERED || order.status == OrderStatus.SHIPPED) {
            throw InvalidOrderStateException("Cannot partially cancel ${order.status.name.lowercase()} order")
        }
    }

    private fun restoreStockForCancelledOrder(order: Order, reason: String?) {
        for (item in order.items) {
            restoreSingleItem(item.productId, item.quantity, order.id, reason)
        }
    }

    private fun restoreSingleItem(productId: Long, quantity: Int, orderId: Long, reason: String?) {
        val product = productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product not found: $productId") }

        val previousStock = product.stockQuantity

        product.stockQuantity += quantity

        productRepository.save(product)

        recordStockAdjustment(
            productId = productId,
            adjustmentType = AdjustmentType.ORDER_CANCELLED,
            quantityChange = quantity,
            previousStock = previousStock,
            newStock = product.stockQuantity,
            reason = reason ?: "Order $orderId cancelled"
        )

        logger.info(
            "Restored stock for product $productId: $previousStock -> ${product.stockQuantity} (+$quantity)"
        )
    }

    private fun recordStockAdjustment(
        productId: Long,
        adjustmentType: AdjustmentType,
        quantityChange: Int,
        previousStock: Int,
        newStock: Int,
        reason: String
    ) {
        val adjustment = StockAdjustment(
            productId = productId,
            adjustmentType = adjustmentType,
            quantityChange = quantityChange,
            previousStock = previousStock,
            newStock = newStock,
            reason = reason
        )

        stockAdjustmentRepository.save(adjustment)
    }

    private fun processRefund(order: Order) {
        try {
            refundService.initiateRefund(order.id, order.totalAmount, order.customerId)
        } catch (e: Exception) {
            logger.error("Failed to initiate refund for order ${order.id}", e)
        }
    }

    private fun recalculateOrderTotal(order: Order) {
        order.totalAmount = order.items
            .map { it.priceAtPurchase.multiply(it.quantity.toBigDecimal()) }
            .fold(java.math.BigDecimal.ZERO) { acc, amount -> acc.add(amount) }
    }

    fun getStockAdjustmentHistory(productId: Long): List<StockAdjustment> {
        return stockAdjustmentRepository.findByProductIdOrderByCreatedAtDesc(productId)
    }
}

data class CancellationResult(
    val orderId: Long,
    val previousStatus: OrderStatus,
    val cancelledAt: LocalDateTime,
    val refundInitiated: Boolean,
    val stockRestored: Boolean
)

data class PartialCancellationResult(
    val orderId: Long,
    val itemId: Long,
    val productId: Long,
    val quantityRestored: Int,
    val orderFullyCancelled: Boolean
)

interface RefundService {
    fun initiateRefund(orderId: Long, amount: java.math.BigDecimal, customerId: Long)
}

interface NotificationService {
    fun sendCancellationNotification(orderId: Long, customerId: Long, reason: String?)
}
