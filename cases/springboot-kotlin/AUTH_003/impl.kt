package com.example.ecommerce.service

import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.OrderStatus
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.exception.OrderNotFoundException
import com.example.ecommerce.exception.InvalidOrderStateException
import org.springframework.security.access.prepost.PreAuthorize
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

    fun findById(orderId: UUID): Order {
        return orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found with id: $orderId") }
    }

    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    fun cancelOrder(orderId: UUID, reason: String?): Order {
        val order = findById(orderId)
        
        validateCancellationEligibility(order)
        
        return order.apply {
            status = OrderStatus.CANCELLED
            cancellationReason = reason
            cancelledAt = LocalDateTime.now()
            lastModifiedAt = LocalDateTime.now()
        }.let { orderRepository.save(it) }
    }

    fun isOwner(orderId: UUID, username: String): Boolean {
        return orderRepository.findById(orderId)
            .map { it.customerEmail == username }
            .orElse(false)
    }

    @PreAuthorize("@orderService.isOwner(#orderId, principal) or hasRole('ADMIN')")
    fun updateOrderStatus(orderId: UUID, newStatus: OrderStatus): Order {
        val order = findById(orderId)
        
        validateStatusTransition(order.status, newStatus)
        
        return order.apply {
            status = newStatus
            lastModifiedAt = LocalDateTime.now()
        }.let { orderRepository.save(it) }
    }

    fun calculateRefundAmount(order: Order): BigDecimal {
        return when (order.status) {
            OrderStatus.PENDING -> order.totalAmount
            OrderStatus.CONFIRMED -> order.totalAmount.multiply(BigDecimal("0.95"))
            OrderStatus.PROCESSING -> order.totalAmount.multiply(BigDecimal("0.80"))
            OrderStatus.SHIPPED -> BigDecimal.ZERO
            else -> BigDecimal.ZERO
        }
    }

    private fun validateCancellationEligibility(order: Order) {
        val nonCancellableStatuses = setOf(
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED,
            OrderStatus.REFUNDED
        )
        
        if (order.status in nonCancellableStatuses) {
            throw InvalidOrderStateException(
                "Cannot cancel order in ${order.status} status"
            )
        }
        
        val hoursSinceCreation = java.time.Duration.between(order.createdAt, LocalDateTime.now()).toHours()
        if (hoursSinceCreation > 24 && order.status == OrderStatus.PROCESSING) {
            throw InvalidOrderStateException(
                "Cannot cancel order after 24 hours in processing status"
            )
        }
    }

    private fun validateStatusTransition(currentStatus: OrderStatus, newStatus: OrderStatus) {
        val validTransitions = mapOf(
            OrderStatus.PENDING to setOf(OrderStatus.CONFIRMED, OrderStatus.CANCELLED),
            OrderStatus.CONFIRMED to setOf(OrderStatus.PROCESSING, OrderStatus.CANCELLED),
            OrderStatus.PROCESSING to setOf(OrderStatus.SHIPPED, OrderStatus.CANCELLED),
            OrderStatus.SHIPPED to setOf(OrderStatus.DELIVERED),
            OrderStatus.DELIVERED to setOf(OrderStatus.REFUNDED)
        )
        
        val allowedStatuses = validTransitions[currentStatus] ?: emptySet()
        if (newStatus !in allowedStatuses) {
            throw InvalidOrderStateException(
                "Invalid status transition from $currentStatus to $newStatus"
            )
        }
    }
}