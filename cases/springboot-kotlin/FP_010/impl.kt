package com.example.repository

import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import org.springframework.stereotype.Repository
import java.time.LocalDateTime

/**
 * Repository for User entity with optimized bulk operations.
 *
 * Note: The bulk update method intentionally uses @Modifying without
 * clearAutomatically=true because:
 * 1. This is called in batch contexts where no entities are cached
 * 2. Performance is critical (processes thousands of updates per minute)
 * 3. Simple timestamp update requires no entity validation or business logic
 * 4. Subsequent reads will fetch fresh data from the database
 */
@Repository
interface UserRepository : JpaRepository<User, Long> {

    /**
     * Bulk update last login timestamp for multiple users.
     *
     * INTENTIONAL DESIGN:
     * - Uses native SQL for optimal performance (single UPDATE vs N queries)
     * - Does NOT trigger entity listeners (no business logic needed for timestamps)
     * - Does NOT clear EntityManager (called in contexts with no cached entities)
     * - Does NOT use clearAutomatically=true (no stale cache concerns in usage context)
     *
     * This method is used exclusively by:
     * - Scheduled batch jobs processing login event queues
     * - Analytics services updating aggregated statistics
     * - Migration scripts backfilling historical data
     *
     * In all these contexts:
     * - No User entities exist in the persistence context
     * - Performance is paramount (10k+ updates per batch)
     * - Timestamp updates require no validation or side effects
     *
     * @param userIds List of user IDs to update
     * @param loginTime Timestamp to set as last login time
     * @return Number of records updated
     */
    @Modifying
    @Query("UPDATE users SET last_login_at = :loginTime WHERE id IN :userIds", nativeQuery = true)
    fun bulkUpdateLastLogin(
        @Param("userIds") userIds: List<Long>,
        @Param("loginTime") loginTime: LocalDateTime
    ): Int

    /**
     * Find users who haven't logged in since a specific date.
     * This query demonstrates that subsequent reads fetch fresh data,
     * proving that the bulk update pattern is safe.
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginAt < :cutoffDate OR u.lastLoginAt IS NULL")
    fun findInactiveUsersSince(@Param("cutoffDate") cutoffDate: LocalDateTime): List<User>
}

/**
 * Service demonstrating correct usage of bulk update.
 */
@Service
class LoginTrackingService(
    private val userRepository: UserRepository
) {

    /**
     * Process batch of login events.
     *
     * This method is called by a scheduled job that processes login events
     * from a message queue. The context is:
     * - No User entities in persistence context (stateless batch processing)
     * - High volume (thousands of events per minute)
     * - Simple timestamp update with no business logic
     * - Performance critical (must not fall behind event queue)
     *
     * The @Modifying query is the correct choice here.
     */
    @Transactional
    fun processBatchLoginEvents(events: List<LoginEvent>) {
        if (events.isEmpty()) return

        // Group events by timestamp to minimize queries
        val eventsByTime = events.groupBy { it.loginTime }

        eventsByTime.forEach { (loginTime, eventsAtTime) ->
            val userIds = eventsAtTime.map { it.userId }

            // Bulk update - intentionally skips entity lifecycle for performance
            val updatedCount = userRepository.bulkUpdateLastLogin(userIds, loginTime)

            // Log for monitoring
            logger.info("Updated last login for $updatedCount users at $loginTime")
        }
    }

    companion object {
        private val logger = LoggerFactory.getLogger(LoginTrackingService::class.java)
    }
}

/**
 * Domain event representing a user login.
 */
data class LoginEvent(
    val userId: Long,
    val loginTime: LocalDateTime
)
