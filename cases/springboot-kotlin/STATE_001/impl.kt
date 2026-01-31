package com.example.orderservice.service

import com.example.orderservice.entity.Order
import com.example.orderservice.entity.OrderStatus
import com.example.orderservice.entity.OrderStatus.*
import com.example.orderservice.repository.OrderRepository
import com.example.orderservice.exception.OrderNotFoundException
import com.example.orderservice.exception.InvalidOrderOperationException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.*

@Service
@Transactional
class OrderService(
    private val orderRepository: OrderRepository
) {

    fun createOrder(customerId: Long, items: List<OrderItem>): Order {
        val totalAmount = calculateTotalAmount(items)
        val order = Order(
            customerId = customerId,
            items = items,
            totalAmount = totalAmount,
            status = PENDING,
            createdAt = LocalDateTime.now()
        )
        return orderRepository.save(order)
    }

    fun confirmOrder(orderId: UUID): Order {
        val order = findOrderById(orderId)
        validateOrderStatusTransition(order.status, CONFIRMED)
        
        order.status = CONFIRMED
        order.confirmedAt = LocalDateTime.now()
        return orderRepository.save(order)
    }

    fun shipOrder(orderId: UUID): Order {
        val order = findOrderById(orderId)
        validateOrderStatusTransition(order.status, SHIPPED)
        
        order.status = SHIPPED
        order.shippedAt = LocalDateTime.now()
        return orderRepository.save(order)
    }

    fun cancelOrder(orderId: UUID, reason: String): Order {
        val order = findOrderById(orderId)
        
        order.cancel()
        order.cancellationReason = reason
        order.cancelledAt = LocalDateTime.now()
        
        return orderRepository.save(order)
    }

    fun deliverOrder(orderId: UUID): Order {
        val order = findOrderById(orderId)
        validateOrderStatusTransition(order.status, DELIVERED)
        
        order.status = DELIVERED
        order.deliveredAt = LocalDateTime.now()
        return orderRepository.save(order)
    }

    @Transactional(readOnly = true)
    fun getOrderById(orderId: UUID): Order = findOrderById(orderId)

    @Transactional(readOnly = true)
    fun getOrdersByCustomer(customerId: Long): List<Order> {
        return orderRepository.findByCustomerIdOrderByCreatedAtDesc(customerId)
    }

    private fun findOrderById(orderId: UUID): Order {
        return orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found with id: $orderId") }
    }

    private fun calculateTotalAmount(items: List<OrderItem>): BigDecimal {
        return items.fold(BigDecimal.ZERO) { total, item ->
            total.add(item.price.multiply(BigDecimal.valueOf(item.quantity.toLong())))
        }
    }

    private fun validateOrderStatusTransition(currentStatus: OrderStatus, targetStatus: OrderStatus) {
        val validTransitions = mapOf(
            PENDING to setOf(CONFIRMED, CANCELLED),
            CONFIRMED to setOf(SHIPPED, CANCELLED),
            SHIPPED to setOf(DELIVERED),
            DELIVERED to emptySet(),
            CANCELLED to emptySet()
        )

        val allowedStatuses = validTransitions[currentStatus] ?: emptySet()
        if (targetStatus !in allowedStatuses) {
            throw InvalidOrderOperationException(
                "Cannot transition from $currentStatus to $targetStatus"
            )
        }
    }
}

data class OrderItem(
    val productId: Long,
    val productName: String,
    val price: BigDecimal,
    val quantity: Int
)