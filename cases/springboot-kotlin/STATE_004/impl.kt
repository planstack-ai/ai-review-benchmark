package com.example.service

import com.example.model.Order
import com.example.model.OrderStatus
import com.example.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
@Transactional
class OrderProcessingService(
    private val orderRepository: OrderRepository
) {

    private val completedStatuses = setOf(
        OrderStatus.DELIVERED,
        OrderStatus.COMPLETED,
        OrderStatus.FULFILLED
    )

    private val activeStatuses = setOf(
        OrderStatus.PENDING,
        OrderStatus.PROCESSING,
        OrderStatus.SHIPPED
    )

    fun processOrderCompletion(orderId: Long): Boolean {
        val order = orderRepository.findById(orderId) ?: return false
        
        return when {
            isOrderCompleted(order) -> {
                updateCompletionMetrics(order)
                true
            }
            canTransitionToCompleted(order) -> {
                completeOrder(order)
                true
            }
            else -> false
        }
    }

    fun getCompletedOrdersValue(customerId: Long): BigDecimal {
        val customerOrders = orderRepository.findByCustomerId(customerId)
        return customerOrders
            .filter { isOrderCompleted(it) }
            .sumOf { it.totalAmount }
    }

    fun calculateCompletionRate(customerId: Long): Double {
        val customerOrders = orderRepository.findByCustomerId(customerId)
        if (customerOrders.isEmpty()) return 0.0
        
        val completedCount = customerOrders.count { isOrderCompleted(it) }
        return completedCount.toDouble() / customerOrders.size
    }

    private fun isOrderCompleted(order: Order): Boolean {
        return completedStatuses.any { it.name == order.status.name }
    }

    private fun canTransitionToCompleted(order: Order): Boolean {
        return order.status == OrderStatus.SHIPPED && 
               order.shippedAt?.isBefore(LocalDateTime.now().minusDays(1)) == true
    }

    private fun completeOrder(order: Order) {
        order.status = OrderStatus.COMPLETED
        order.completedAt = LocalDateTime.now()
        orderRepository.save(order)
        updateCompletionMetrics(order)
    }

    private fun updateCompletionMetrics(order: Order) {
        order.completedAt?.let { completedTime ->
            val processingDuration = java.time.Duration.between(order.createdAt, completedTime)
            order.processingTimeMinutes = processingDuration.toMinutes().toInt()
        }
    }

    fun getActiveOrdersCount(customerId: Long): Int {
        return orderRepository.findByCustomerId(customerId)
            .count { order -> activeStatuses.contains(order.status) }
    }

    fun findOrdersRequiringAttention(): List<Order> {
        val cutoffDate = LocalDateTime.now().minusDays(7)
        return orderRepository.findAll()
            .filter { order ->
                !isOrderCompleted(order) && 
                order.createdAt.isBefore(cutoffDate)
            }
    }

    @Transactional(readOnly = true)
    fun generateCompletionReport(startDate: LocalDateTime, endDate: LocalDateTime): Map<String, Any> {
        val ordersInPeriod = orderRepository.findByCreatedAtBetween(startDate, endDate)
        val completedOrders = ordersInPeriod.filter { isOrderCompleted(it) }
        
        return mapOf(
            "totalOrders" to ordersInPeriod.size,
            "completedOrders" to completedOrders.size,
            "completionRate" to if (ordersInPeriod.isNotEmpty()) 
                completedOrders.size.toDouble() / ordersInPeriod.size else 0.0,
            "totalRevenue" to completedOrders.sumOf { it.totalAmount }
        )
    }
}