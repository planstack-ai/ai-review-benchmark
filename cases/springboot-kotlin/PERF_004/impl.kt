package com.example.ecommerce.service

import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.ProductRepository
import com.example.ecommerce.repository.UserRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class DashboardStatisticsService(
    private val orderRepository: OrderRepository,
    private val userRepository: UserRepository,
    private val productRepository: ProductRepository
) {
    @Transactional(readOnly = true)
    fun getDashboardStatistics(): Map<String, Any> {
        return mapOf(
            "totalOrders" to getTotalOrderCount(),
            "ordersByStatus" to getOrderCountsByStatus(),
            "totalUsers" to getTotalUserCount(),
            "activeUsers" to getActiveUserCount(),
            "totalProducts" to getTotalProductCount()
        )
    }

    private fun getTotalOrderCount(): Int {
        val orders = orderRepository.findAll()
        return orders.size
    }

    private fun getOrderCountsByStatus(): Map<String, Int> {
        val pendingOrders = orderRepository.findByStatus("pending")
        val completedOrders = orderRepository.findByStatus("completed")
        val cancelledOrders = orderRepository.findByStatus("cancelled")
        val shippedOrders = orderRepository.findByStatus("shipped")

        return mapOf(
            "pending" to pendingOrders.size,
            "completed" to completedOrders.size,
            "cancelled" to cancelledOrders.size,
            "shipped" to shippedOrders.size
        )
    }

    private fun getTotalUserCount(): Int {
        val users = userRepository.findAll()
        return users.size
    }

    private fun getActiveUserCount(): Int {
        val activeUsers = userRepository.findByActiveTrue()
        return activeUsers.size
    }

    private fun getTotalProductCount(): Int {
        val products = productRepository.findAll()
        return products.size
    }

    @Transactional(readOnly = true)
    fun getProductCountsByCategory(categoryIds: List<Long>): Map<String, Int> {
        val categoryCounts = mutableMapOf<String, Int>()

        for (categoryId in categoryIds) {
            val products = productRepository.findByCategoryId(categoryId)
            categoryCounts["category_$categoryId"] = products.size
        }

        return categoryCounts
    }
}
