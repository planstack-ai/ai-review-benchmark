package com.example.orderservice.service

import com.example.orderservice.entity.Order
import com.example.orderservice.entity.OrderStatus
import com.example.orderservice.entity.OrderStatusTransition
import com.example.orderservice.repository.OrderRepository
import com.example.orderservice.repository.OrderStatusTransitionRepository
import com.example.orderservice.constants.OrderConstants
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal

/**
 * This is a CORRECTLY implemented order service with proper state machine.
 * No bugs - should NOT trigger any critical or major issues.
 */
@Service
@Transactional
class OrderServiceImpl(
    private val orderRepository: OrderRepository,
    private val transitionRepository: OrderStatusTransitionRepository
) : OrderService {

    override fun createOrder(customerId: Long, totalAmount: BigDecimal): Order {
        validateOrderCreationInput(customerId, totalAmount)

        val order = Order().apply {
            this.customerId = customerId
            this.totalAmount = totalAmount
            this.status = OrderStatus.PENDING
        }

        return orderRepository.save(order)
    }

    override fun updateOrderStatus(orderId: Long, newStatus: OrderStatus): Order {
        val order = findOrderById(orderId)
        val currentStatus = order.status
            ?: throw IllegalStateException("Order has invalid status")

        validateStatusTransition(currentStatus, newStatus)

        order.status = newStatus
        return orderRepository.save(order)
    }

    override fun getAllowedTransitions(currentStatus: OrderStatus): List<OrderStatus> {
        val transitions = transitionRepository.findByFromStatusAndAllowedTrue(currentStatus)

        if (transitions.isEmpty()) {
            return getDefaultAllowedTransitions(currentStatus)
        }

        return transitions.mapNotNull { it.toStatus }
    }

    override fun isTransitionAllowed(fromStatus: OrderStatus, toStatus: OrderStatus): Boolean {
        val transition = transitionRepository.findByFromStatusAndToStatus(fromStatus, toStatus)

        if (transition.isPresent) {
            return transition.get().allowed ?: false
        }

        return isDefaultTransitionAllowed(fromStatus, toStatus)
    }

    private fun validateOrderCreationInput(customerId: Long, totalAmount: BigDecimal) {
        if (customerId <= 0) {
            throw IllegalArgumentException("Customer ID must be positive")
        }
        if (totalAmount.compareTo(BigDecimal.ZERO) < 0) {
            throw IllegalArgumentException("Total amount cannot be negative")
        }
    }

    private fun findOrderById(orderId: Long): Order {
        return orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found with ID: $orderId") }
    }

    private fun validateStatusTransition(fromStatus: OrderStatus, toStatus: OrderStatus) {
        if (!isTransitionAllowed(fromStatus, toStatus)) {
            throw IllegalStateException("Invalid status transition from $fromStatus to $toStatus")
        }
    }

    private fun getDefaultAllowedTransitions(currentStatus: OrderStatus): List<OrderStatus> {
        val allowedStatuses = OrderConstants.DEFAULT_TRANSITIONS[currentStatus]
        return allowedStatuses?.toList() ?: emptyList()
    }

    private fun isDefaultTransitionAllowed(fromStatus: OrderStatus, toStatus: OrderStatus): Boolean {
        val allowedTransitions = OrderConstants.DEFAULT_TRANSITIONS[fromStatus]
        return allowedTransitions?.contains(toStatus) ?: false
    }
}
