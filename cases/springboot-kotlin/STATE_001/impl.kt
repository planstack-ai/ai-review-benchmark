package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderStatus
import com.example.order.exception.InvalidStateTransitionException
import com.example.order.exception.OrderNotFoundException
import com.example.order.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional
class OrderStateService(
    private val orderRepository: OrderRepository
) {
    companion object {
        private val CANCELLABLE_STATES = setOf(OrderStatus.PENDING, OrderStatus.CONFIRMED)
    }

    // BUG: Should validate state before cancellation
    // Only PENDING or CONFIRMED orders should be cancellable
    fun cancelOrder(orderId: Long): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        // Missing state validation - should check if order.status in CANCELLABLE_STATES
        order.status = OrderStatus.CANCELLED
        order.cancelledAt = LocalDateTime.now()

        return orderRepository.save(order)
    }

    fun confirmOrder(orderId: Long): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        validateStateTransition(order, OrderStatus.CONFIRMED)

        order.status = OrderStatus.CONFIRMED
        order.confirmedAt = LocalDateTime.now()

        return orderRepository.save(order)
    }

    fun shipOrder(orderId: Long): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        validateStateTransition(order, OrderStatus.SHIPPED)

        order.status = OrderStatus.SHIPPED
        order.shippedAt = LocalDateTime.now()

        return orderRepository.save(order)
    }

    fun completeOrder(orderId: Long): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        validateStateTransition(order, OrderStatus.COMPLETED)

        order.status = OrderStatus.COMPLETED
        order.completedAt = LocalDateTime.now()

        return orderRepository.save(order)
    }

    private fun validateStateTransition(order: Order, targetStatus: OrderStatus) {
        val allowedTransitions = mapOf(
            OrderStatus.PENDING to setOf(OrderStatus.CONFIRMED, OrderStatus.CANCELLED),
            OrderStatus.CONFIRMED to setOf(OrderStatus.SHIPPED, OrderStatus.CANCELLED),
            OrderStatus.SHIPPED to setOf(OrderStatus.COMPLETED),
            OrderStatus.COMPLETED to emptySet<OrderStatus>(),
            OrderStatus.CANCELLED to emptySet<OrderStatus>()
        )

        val allowed = allowedTransitions[order.status] ?: emptySet()
        if (targetStatus !in allowed) {
            throw InvalidStateTransitionException(
                "Cannot transition from ${order.status} to $targetStatus"
            )
        }
    }

    fun getOrderStatus(orderId: Long): OrderStatus {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }
        return order.status
    }

    fun canCancel(orderId: Long): Boolean {
        val order = orderRepository.findById(orderId).orElse(null)
            ?: return false
        return order.status in CANCELLABLE_STATES
    }
}
