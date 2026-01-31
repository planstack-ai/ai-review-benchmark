package com.example.order.service

import com.example.order.entity.Order
import com.example.order.repository.OrderRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

interface OrderRepository : org.springframework.data.jpa.repository.JpaRepository<Order, Long> {

    // BUG: @Modifying queries bypass JPA entity lifecycle
    // @EntityListeners callbacks (including @PreUpdate) are NOT invoked
    // Audit trail will NOT be created for these bulk updates
    // This violates compliance requirements
    @Modifying
    @Query("UPDATE Order o SET o.status = :status WHERE o.createdAt < :cutoffDate")
    fun bulkUpdateStatus(status: String, cutoffDate: LocalDateTime): Int

    fun findByCreatedAtBeforeAndStatusNot(cutoffDate: LocalDateTime, status: String): List<Order>
}

@Service
class OrderArchivalService(
    private val orderRepository: OrderRepository
) {

    @Transactional
    fun archiveOldOrders(daysOld: Int): ArchivalResult {
        val cutoffDate = LocalDateTime.now().minusDays(daysOld.toLong())

        // BUG: Using bulk update query that bypasses entity listeners
        // The @PreUpdate callback in OrderAuditListener will NOT be triggered
        // No audit logs will be created despite compliance requirement
        val count = orderRepository.bulkUpdateStatus("ARCHIVED", cutoffDate)

        return ArchivalResult(
            archivedCount = count,
            processedAt = LocalDateTime.now()
        )
    }

    @Transactional
    fun getArchivableCandidates(daysOld: Int): List<Order> {
        val cutoffDate = LocalDateTime.now().minusDays(daysOld.toLong())
        return orderRepository.findByCreatedAtBeforeAndStatusNot(cutoffDate, "ARCHIVED")
    }
}

data class ArchivalResult(
    val archivedCount: Int,
    val processedAt: LocalDateTime
)
