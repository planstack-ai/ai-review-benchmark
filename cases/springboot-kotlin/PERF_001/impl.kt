package com.example.ecommerce.service

import com.example.ecommerce.entity.Order
import com.example.ecommerce.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class OrderReportService(
    private val orderRepository: OrderRepository
) {
    private var startDate: LocalDateTime = LocalDateTime.now().minusDays(30)
    private var endDate: LocalDateTime = LocalDateTime.now()

    fun setDateRange(start: LocalDateTime, end: LocalDateTime) {
        this.startDate = start
        this.endDate = end
    }

    @Transactional(readOnly = true)
    fun generateSummaryReport(): Map<String, Any> {
        val orders = fetchOrders()
        if (orders.isEmpty()) {
            return emptyReport()
        }

        return mapOf(
            "totalOrders" to orders.size,
            "totalRevenue" to calculateTotalRevenue(orders),
            "productBreakdown" to generateProductBreakdown(orders),
            "averageOrderValue" to calculateAverageOrderValue(orders),
            "topProducts" to identifyTopProducts(orders)
        )
    }

    @Transactional(readOnly = true)
    fun exportDetailedReport(): List<Map<String, Any?>> {
        val orders = fetchOrdersWithDetails()
        return orders.map { order -> buildOrderSummary(order) }
    }

    private fun fetchOrders(): List<Order> {
        return orderRepository.findByCreatedAtBetween(startDate, endDate)
    }

    private fun fetchOrdersWithDetails(): List<Order> {
        return orderRepository.findByCreatedAtBetween(startDate, endDate)
    }

    private fun buildOrderSummary(order: Order): Map<String, Any?> {
        val itemDetails = collectItemDetails(order)

        return mapOf(
            "orderId" to order.id,
            "orderDate" to order.createdAt,
            "totalAmount" to order.totalCents,
            "itemsCount" to order.items.size,
            "itemDetails" to itemDetails
        )
    }

    private fun collectItemDetails(order: Order): List<Map<String, Any?>> {
        val details = mutableListOf<Map<String, Any?>>()

        order.items.forEach { item ->
            details.add(mapOf(
                "productName" to item.product.name,
                "quantity" to item.quantity,
                "unitPrice" to item.priceCents,
                "totalPrice" to item.priceCents * item.quantity
            ))
        }

        return details
    }

    private fun calculateTotalRevenue(orders: List<Order>): Long {
        return orders.sumOf { it.totalCents.toLong() }
    }

    private fun calculateAverageOrderValue(orders: List<Order>): Double {
        if (orders.isEmpty()) return 0.0
        return calculateTotalRevenue(orders).toDouble() / orders.size
    }

    private fun generateProductBreakdown(orders: List<Order>): Map<String, Long> {
        val productSales = mutableMapOf<String, Long>()

        orders.forEach { order ->
            order.items.forEach { item ->
                val productName = item.product.name
                val itemTotal = item.priceCents.toLong() * item.quantity
                productSales.merge(productName, itemTotal, Long::plus)
            }
        }

        return productSales
    }

    private fun identifyTopProducts(orders: List<Order>, limit: Int = 5): Map<String, Long> {
        return generateProductBreakdown(orders)
            .entries
            .sortedByDescending { it.value }
            .take(limit)
            .associate { it.key to it.value }
    }

    private fun emptyReport(): Map<String, Any> {
        return mapOf(
            "totalOrders" to 0,
            "totalRevenue" to 0L,
            "productBreakdown" to emptyMap<String, Long>(),
            "averageOrderValue" to 0.0,
            "topProducts" to emptyMap<String, Long>()
        )
    }
}
