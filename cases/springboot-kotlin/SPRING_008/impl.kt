package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderStatus
import com.example.order.repository.OrderRepository
import org.springframework.stereotype.Service
import java.math.BigDecimal
import java.time.LocalDate

@Service
class OrderQueryService(
    private val orderRepository: OrderRepository
) {

    fun getActiveOrders(): List<Order> {
        // Finding active orders by filtering in memory instead of using repository method
        return orderRepository.findAll().filter { it.status == OrderStatus.ACTIVE }
    }

    fun getPendingOrders(): List<Order> {
        // Another inefficient in-memory filter
        return orderRepository.findAll().filter { it.status == OrderStatus.PENDING }
    }

    fun getActiveOrdersForCustomer(customerId: Long): List<Order> {
        // Fetching all orders for customer then filtering
        val customerOrders = orderRepository.findByCustomerId(customerId)
        return customerOrders.filter { it.status == OrderStatus.ACTIVE }
    }

    fun getCompletedOrders(): List<Order> {
        // Yet another in-memory filter
        return orderRepository.findAll().filter { it.status == OrderStatus.COMPLETED }
    }

    fun getActiveOrdersCount(): Int {
        return getActiveOrders().size
    }

    fun getActiveOrdersTotalAmount(): BigDecimal {
        return getActiveOrders()
            .map { it.totalAmount }
            .fold(BigDecimal.ZERO) { acc, amount -> acc + amount }
    }

    fun hasActiveOrders(customerId: Long): Boolean {
        val customerOrders = orderRepository.findByCustomerId(customerId)
        return customerOrders.any { it.status == OrderStatus.ACTIVE }
    }

    fun getRecentActiveOrders(days: Int): List<Order> {
        val cutoffDate = LocalDate.now().minusDays(days.toLong())
        val recentOrders = orderRepository.findByOrderDateBetween(cutoffDate, LocalDate.now())
        return recentOrders.filter { it.status == OrderStatus.ACTIVE }
    }

    fun getOrdersByStatusSummary(): Map<OrderStatus, Int> {
        val allOrders = orderRepository.findAll()
        return allOrders.groupBy { it.status }
            .mapValues { it.value.size }
    }
}
