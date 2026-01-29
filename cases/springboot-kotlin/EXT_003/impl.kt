package com.example.ecommerce.service

import com.example.ecommerce.dto.OrderRequest
import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.OrderItem
import com.example.ecommerce.repository.OrderItemRepository
import com.example.ecommerce.repository.OrderRepository
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.*

@Service
class OrderProcessingService(
    private val orderRepository: OrderRepository,
    private val orderItemRepository: OrderItemRepository,
    private val inventoryService: InventoryService,
    private val paymentGatewayService: PaymentGatewayService,
    private val shippingService: ShippingService,
    private val notificationService: NotificationService
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Transactional
    fun processOrder(request: OrderRequest): Order {
        logger.info("Processing order for customer: ${request.customerId}")

        val order = createOrder(request)
        val savedOrder = orderRepository.save(order)

        val items = createOrderItems(savedOrder, request)
        orderItemRepository.saveAll(items)

        inventoryService.reserveStock(request.items)

        val totalAmount = calculateTotal(items)
        val transactionId = paymentGatewayService.chargeCard(
            request.paymentToken,
            totalAmount
        )

        savedOrder.paymentTransactionId = transactionId
        savedOrder.status = "PAID"

        val trackingNumber = shippingService.createShipment(savedOrder)
        savedOrder.trackingNumber = trackingNumber
        savedOrder.status = "PROCESSING"

        orderRepository.save(savedOrder)

        notificationService.sendOrderConfirmation(request.customerId, savedOrder.id!!)

        logger.info("Order processed successfully: ${savedOrder.id}")
        return savedOrder
    }

    @Transactional
    fun createOrderWithPayment(request: OrderRequest): Order {
        val order = createOrder(request)
        val savedOrder = orderRepository.save(order)

        val items = createOrderItems(savedOrder, request)
        orderItemRepository.saveAll(items)

        val total = calculateTotal(items)

        val paymentId = paymentGatewayService.chargeCard(request.paymentToken, total)
        savedOrder.paymentTransactionId = paymentId

        inventoryService.decrementStock(request.items)

        savedOrder.status = "COMPLETED"
        return orderRepository.save(savedOrder)
    }

    private fun createOrder(request: OrderRequest): Order {
        return Order(
            id = UUID.randomUUID().toString(),
            customerId = request.customerId,
            status = "PENDING",
            createdAt = LocalDateTime.now()
        )
    }

    private fun createOrderItems(order: Order, request: OrderRequest): List<OrderItem> {
        return request.items.map { itemReq ->
            OrderItem(
                orderId = order.id!!,
                productId = itemReq.productId,
                quantity = itemReq.quantity,
                priceCents = itemReq.priceCents
            )
        }
    }

    private fun calculateTotal(items: List<OrderItem>): BigDecimal {
        return items
            .map { BigDecimal.valueOf(it.priceCents.toLong() * it.quantity) }
            .fold(BigDecimal.ZERO) { acc, item -> acc.add(item) }
            .divide(BigDecimal.valueOf(100))
    }
}
