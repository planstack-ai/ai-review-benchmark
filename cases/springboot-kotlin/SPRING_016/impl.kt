package com.example.order.service

import com.example.order.entity.Order
import com.example.order.repository.OrderRepository
import org.springframework.stereotype.Service
import java.math.BigDecimal
import java.time.LocalDateTime

data class OrderSummary(
    val orderId: Long,
    val totalAmount: BigDecimal,
    val orderDate: LocalDateTime
)

data class SalesReport(
    val orders: List<OrderSummary>,
    val totalOrders: Int,
    val totalRevenue: BigDecimal,
    val generatedAt: LocalDateTime
)

@Service
class SalesReportService(
    private val orderRepository: OrderRepository
) {

    fun generateSalesReport(): List<OrderSummary> {
        // BUG: Loading full Order entities when only 3 fields are needed
        // This loads ALL fields including:
        // - customerEmail, customerName, customerPhone
        // - billingAddress, shippingAddress (TEXT fields)
        // - notes (TEXT field)
        // - ALL related OrderItems (EAGER fetch)
        // - Each item's productDescription (TEXT field)
        //
        // For 50,000 orders with 5 items each:
        // - Loads 50,000 * 2KB = 100MB+ of unnecessary data
        // - Takes several seconds to fetch and construct entities
        // - High memory pressure, potential OutOfMemoryError
        // - Slow response time
        //
        // Should use projection to select only: id, total_amount, created_at
        val orders = orderRepository.findAll()
        return orders.map { OrderSummary(
            orderId = it.id!!,
            totalAmount = it.totalAmount,
            orderDate = it.createdAt
        ) }
    }

    fun generateFullReport(): SalesReport {
        val summaries = generateSalesReport()

        return SalesReport(
            orders = summaries,
            totalOrders = summaries.size,
            totalRevenue = summaries.sumOf { it.totalAmount },
            generatedAt = LocalDateTime.now()
        )
    }
}
