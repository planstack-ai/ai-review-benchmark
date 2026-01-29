package com.example.ecommerce.service

import com.example.ecommerce.entity.Order
import com.example.ecommerce.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.YearMonth

@Service
class SalesReportService(
    private val orderRepository: OrderRepository
) {
    @Transactional(readOnly = true)
    fun generateMonthlySalesReport(month: YearMonth): Map<String, Any> {
        val startOfMonth = month.atDay(1).atStartOfDay()
        val endOfMonth = month.atEndOfMonth().atTime(23, 59, 59)

        val allOrders = orderRepository.findAll()

        val monthlyOrders = allOrders.filter { order ->
            !order.createdAt.isBefore(startOfMonth) && !order.createdAt.isAfter(endOfMonth)
        }

        return mapOf(
            "month" to month.toString(),
            "totalOrders" to monthlyOrders.size,
            "totalRevenue" to calculateTotalRevenue(monthlyOrders),
            "ordersByStatus" to countOrdersByStatus(monthlyOrders),
            "averageOrderValue" to calculateAverageOrderValue(monthlyOrders)
        )
    }

    @Transactional(readOnly = true)
    fun generateYearlySalesReport(year: Int): Map<String, Any> {
        val allOrders = orderRepository.findAll()

        val yearlyOrders = allOrders.filter { order ->
            order.createdAt.year == year
        }

        return mapOf(
            "year" to year,
            "totalOrders" to yearlyOrders.size,
            "totalRevenue" to calculateTotalRevenue(yearlyOrders),
            "monthlyBreakdown" to generateMonthlyBreakdown(yearlyOrders)
        )
    }

    @Transactional(readOnly = true)
    fun exportAllOrdersForAudit(): List<Map<String, Any?>> {
        val allOrders = orderRepository.findAll()
        return allOrders.map { orderToMap(it) }
    }

    private fun calculateTotalRevenue(orders: List<Order>): Long =
        orders.sumOf { it.totalCents.toLong() }

    private fun countOrdersByStatus(orders: List<Order>): Map<String, Long> =
        orders.groupingBy { it.status }.eachCount().mapValues { it.value.toLong() }

    private fun calculateAverageOrderValue(orders: List<Order>): Double {
        if (orders.isEmpty()) return 0.0
        return calculateTotalRevenue(orders).toDouble() / orders.size
    }

    private fun generateMonthlyBreakdown(orders: List<Order>): Map<Int, Long> =
        orders.groupBy { it.createdAt.monthValue }
            .mapValues { (_, monthOrders) -> calculateTotalRevenue(monthOrders) }

    private fun orderToMap(order: Order): Map<String, Any?> = mapOf(
        "id" to order.id,
        "userId" to order.userId,
        "totalCents" to order.totalCents,
        "status" to order.status,
        "createdAt" to order.createdAt
    )
}
