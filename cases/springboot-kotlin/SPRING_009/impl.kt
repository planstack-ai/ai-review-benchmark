package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderStatus
import com.example.order.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class OrderValidationService(
    private val orderRepository: OrderRepository
) {

    fun canProcessOrder(orderId: Long): Boolean {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        // Using string comparison instead of enum comparison
        return order.status.name == "PENDING" || order.status.name == "CONFIRMED"
    }

    fun isPendingOrder(order: Order): Boolean {
        // String literal comparison instead of type-safe enum comparison
        return order.status.name == "PENDING"
    }

    fun canCancelOrder(orderId: Long): Boolean {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        // String comparison prone to typos
        return order.status.name == "PENDING" ||
               order.status.name == "CONFIRMED" ||
               order.status.name == "PROCESSING"
    }

    @Transactional
    fun confirmOrder(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        if (order.status.name != "PENDING") {
            throw IllegalStateException("Only pending orders can be confirmed")
        }

        order.status = OrderStatus.CONFIRMED
        orderRepository.save(order)
    }

    @Transactional
    fun shipOrder(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        if (order.status.name != "PROCESSING") {
            throw IllegalStateException("Only processing orders can be shipped")
        }

        order.status = OrderStatus.SHIPPED
        orderRepository.save(order)
    }

    fun isOrderModifiable(order: Order): Boolean {
        // Multiple string comparisons
        return order.status.name == "PENDING" || order.status.name == "CONFIRMED"
    }

    fun getOrderStatusDescription(order: Order): String {
        return when (order.status.name) {
            "PENDING" -> "Order is awaiting confirmation"
            "CONFIRMED" -> "Order has been confirmed"
            "PROCESSING" -> "Order is being processed"
            "SHIPPED" -> "Order has been shipped"
            "DELIVERED" -> "Order has been delivered"
            "CANCELLED" -> "Order has been cancelled"
            else -> "Unknown status"
        }
    }

    fun canRefund(orderId: Long): Boolean {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        return order.status.name == "DELIVERED" || order.status.name == "CANCELLED"
    }
}
