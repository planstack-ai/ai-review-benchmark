package com.example.ecommerce.service

import com.example.ecommerce.entity.OrderItem
import com.example.ecommerce.repository.OrderItemRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime
import java.util.*

@Service
class SalesAnalyticsService(
    private val orderItemRepository: OrderItemRepository
) {
    @Transactional(readOnly = true)
    fun getRevenueByCategory(): Map<Long, Long> {
        val allItems = orderItemRepository.findAll()

        return allItems
            .groupBy { it.product.category.id }
            .mapValues { (_, items) ->
                items.sumOf { it.priceCents.toLong() * it.quantity }
            }
    }

    @Transactional(readOnly = true)
    fun getTopSellingProducts(limit: Int): List<Map<String, Any?>> {
        val allItems = orderItemRepository.findAll()

        val productQuantities = allItems
            .groupBy { it.product.id }
            .mapValues { (_, items) -> items.sumOf { it.quantity.toLong() } }

        return productQuantities.entries
            .sortedByDescending { it.value }
            .take(limit)
            .map { entry ->
                mapOf(
                    "productId" to entry.key,
                    "totalQuantity" to entry.value
                )
            }
    }

    @Transactional(readOnly = true)
    fun getMonthlySalesTrend(year: Int): Map<String, Long> {
        val allItems = orderItemRepository.findAll()

        return allItems
            .filter { it.createdAt.year == year }
            .groupBy { String.format("%d-%02d", year, it.createdAt.monthValue) }
            .toSortedMap()
            .mapValues { (_, items) ->
                items.sumOf { it.priceCents.toLong() * it.quantity }
            }
    }

    @Transactional(readOnly = true)
    fun getSalesAnalytics(startDate: LocalDateTime, endDate: LocalDateTime): Map<String, Any> {
        val items = orderItemRepository.findByCreatedAtBetween(startDate, endDate)

        val totalRevenue = items.sumOf { it.priceCents.toLong() * it.quantity }
        val totalQuantity = items.sumOf { it.quantity.toLong() }
        val uniqueOrders = items.map { it.order.id }.distinct().count()
        val averageOrderValue = if (uniqueOrders > 0) totalRevenue.toDouble() / uniqueOrders else 0.0

        return mapOf(
            "totalRevenue" to totalRevenue,
            "totalQuantity" to totalQuantity,
            "averageOrderValue" to averageOrderValue,
            "itemCount" to items.size
        )
    }

    @Transactional(readOnly = true)
    fun getProductPerformanceReport(): List<Map<String, Any?>> {
        val allItems = orderItemRepository.findAll()

        return allItems
            .groupBy { it.product.id }
            .map { (productId, items) ->
                val totalRevenue = items.sumOf { it.priceCents.toLong() * it.quantity }
                val orderCount = items.size
                mapOf(
                    "productId" to productId,
                    "totalRevenue" to totalRevenue,
                    "orderCount" to orderCount,
                    "averageRevenue" to if (orderCount > 0) totalRevenue.toDouble() / orderCount else 0.0
                )
            }
            .sortedByDescending { it["totalRevenue"] as Long }
    }
}
