package com.example.ecommerce.service

import com.example.ecommerce.entity.User
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.UserRepository
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime
import java.time.temporal.ChronoUnit

@Service
class UserMetricsBatchService(
    private val userRepository: UserRepository,
    private val orderRepository: OrderRepository
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Scheduled(cron = "0 0 2 * * *")
    @Transactional
    fun updateAllUserMetrics(): Map<String, Any> {
        logger.info("Starting bulk user metrics update")

        val activeUsers = userRepository.findByActiveTrue()
        var processed = 0
        var failed = 0

        activeUsers.forEach { user ->
            try {
                updateUserMetrics(user.id!!)
                processed++
            } catch (e: Exception) {
                logger.error("Failed to update metrics for user: ${user.id}", e)
                failed++
            }
        }

        val result = mapOf(
            "totalUsers" to activeUsers.size,
            "processed" to processed,
            "failed" to failed
        )

        logger.info("Completed bulk user metrics update: $result")
        return result
    }

    @Transactional
    fun updateUserMetrics(userId: Long) {
        val user = userRepository.findById(userId)
            .orElseThrow { IllegalArgumentException("User not found: $userId") }

        val orderCount = orderRepository.countByUserId(userId)

        val engagementScore = calculateEngagementScore(orderCount, user.lastActive)

        user.orderCount = orderCount.toInt()
        user.engagementScore = engagementScore

        userRepository.save(user)
    }

    @Transactional
    fun recalculateAllEngagementScores() {
        val allUsers = userRepository.findByActiveTrue()

        allUsers.forEach { user ->
            val orderCount = orderRepository.countByUserId(user.id!!)
            val score = calculateEngagementScore(orderCount, user.lastActive)

            userRepository.updateEngagementScore(user.id!!, score)
        }
    }

    @Transactional
    fun generateUserActivityReport(): Map<String, Any> {
        val users = userRepository.findByActiveTrue()

        var highEngagement = 0
        var mediumEngagement = 0
        var lowEngagement = 0
        var totalOrders = 0L

        users.forEach { user ->
            val orderCount = orderRepository.countByUserId(user.id!!)
            totalOrders += orderCount

            val score = calculateEngagementScore(orderCount, user.lastActive)
            when {
                score >= 80 -> highEngagement++
                score >= 50 -> mediumEngagement++
                else -> lowEngagement++
            }
        }

        return mapOf(
            "totalUsers" to users.size,
            "totalOrders" to totalOrders,
            "highEngagement" to highEngagement,
            "mediumEngagement" to mediumEngagement,
            "lowEngagement" to lowEngagement,
            "averageOrdersPerUser" to if (users.isEmpty()) 0.0 else totalOrders.toDouble() / users.size
        )
    }

    private fun calculateEngagementScore(orderCount: Long, lastActive: LocalDateTime?): Int {
        var score = 0

        score += when {
            orderCount >= 10 -> 50
            orderCount >= 5 -> 30
            orderCount >= 1 -> 10
            else -> 0
        }

        if (lastActive != null) {
            val daysSinceActive = ChronoUnit.DAYS.between(lastActive, LocalDateTime.now())
            score += when {
                daysSinceActive <= 7 -> 50
                daysSinceActive <= 30 -> 30
                daysSinceActive <= 90 -> 10
                else -> 0
            }
        }

        return minOf(score, 100)
    }
}
