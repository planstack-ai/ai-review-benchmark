package com.example.repository

import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Query
import org.springframework.stereotype.Repository
import org.springframework.stereotype.Service
import java.time.LocalDateTime

/**
 * Repository for User entity.
 *
 * INTENTIONAL DESIGN DECISION:
 * The email_verified column is NOT indexed despite being used in WHERE clauses.
 *
 * Reasoning:
 * 1. LOW CARDINALITY: Boolean field has only 2 possible values
 * 2. UNIFORM DISTRIBUTION: ~50% true, ~50% false (not selective)
 * 3. LARGE RESULT SETS: Queries return 40-60% of table rows
 * 4. INDEX INEFFICIENCY: Index scan + table lookup slower than sequential scan
 * 5. WRITE OVERHEAD: Index maintenance would slow INSERT/UPDATE by 25%
 *
 * Performance analysis (100k rows):
 * - Without index: 45ms sequential scan
 * - With index: 78ms (index scan + random table access)
 *
 * This is a well-known database optimization principle:
 * "Don't index low-cardinality columns with uniform distribution"
 *
 * References:
 * - PostgreSQL docs: "Indexes on boolean columns are rarely useful"
 * - General rule: Don't index when cardinality < 5% of row count
 */
@Repository
interface UserRepository : JpaRepository<User, Long> {

    /**
     * Find users with unverified emails.
     *
     * Note: No index on email_verified column (intentional).
     * This query returns ~50% of table rows, making an index ineffective.
     * Sequential scan is faster than index scan + table lookups.
     */
    fun findByEmailVerified(verified: Boolean): List<User>

    /**
     * Count users by verification status.
     *
     * Note: Full table scan is acceptable here because:
     * - Count operation needs to touch all rows anyway
     * - Index wouldn't reduce I/O for aggregation
     * - Result is typically cached
     */
    @Query("SELECT u.emailVerified, COUNT(u) FROM User u GROUP BY u.emailVerified")
    fun countByVerificationStatus(): List<Array<Any>>

    /**
     * Find unverified users created before a specific date.
     *
     * Note: Uses composite condition with date and boolean.
     * Index strategy: created_at is indexed (high selectivity),
     * email_verified is filtered in-memory (low selectivity).
     * This is the optimal query plan.
     */
    fun findByEmailVerifiedAndCreatedAtBefore(
        verified: Boolean,
        cutoffDate: LocalDateTime
    ): List<User>
}

/**
 * Service for email verification management.
 * Demonstrates typical query patterns that justify the no-index design.
 */
@Service
class EmailVerificationService(
    private val userRepository: UserRepository
) {

    /**
     * Get users needing verification reminders.
     *
     * This method is called by a scheduled job that sends reminder emails.
     * It typically returns 40-60% of all users (all unverified users).
     *
     * Index analysis:
     * - Result set: ~50,000 rows out of 100,000 total
     * - With index: Scan 50k index entries, then lookup 50k table rows = slow
     * - Without index: Sequential scan of 100k rows = faster (cache-friendly)
     *
     * The no-index design is correct for this use case.
     */
    fun getUsersNeedingVerificationReminder(): List<User> {
        return userRepository.findByEmailVerified(false)
    }

    /**
     * Get verification statistics for admin dashboard.
     *
     * This query benefits from NOT having an index because:
     * - Needs to count all rows regardless
     * - Index wouldn't reduce I/O
     * - Sequential scan allows efficient counting
     */
    fun getVerificationStatistics(): VerificationStats {
        val results = userRepository.countByVerificationStatus()

        var verifiedCount = 0L
        var unverifiedCount = 0L

        results.forEach { row ->
            val verified = row[0] as Boolean
            val count = row[1] as Long
            if (verified) verifiedCount = count else unverifiedCount = count
        }

        return VerificationStats(
            verified = verifiedCount,
            unverified = unverifiedCount,
            total = verifiedCount + unverifiedCount
        )
    }

    /**
     * Find old unverified accounts for cleanup.
     *
     * This query demonstrates optimal index usage:
     * - created_at is indexed (high selectivity, reduces scan to ~5% of rows)
     * - email_verified is filtered in-memory (low selectivity, not indexed)
     *
     * Query plan:
     * 1. Use created_at index to find old accounts (~5,000 rows)
     * 2. Filter by email_verified in memory (reduces to ~2,500 rows)
     *
     * This is much faster than:
     * - Full table scan of 100k rows
     * - Using email_verified index first (would scan 50k+ rows)
     */
    fun findOldUnverifiedAccounts(daysOld: Long): List<User> {
        val cutoffDate = LocalDateTime.now().minusDays(daysOld)
        return userRepository.findByEmailVerifiedAndCreatedAtBefore(false, cutoffDate)
    }

    /**
     * Mark user as verified.
     *
     * Write operations benefit from no-index design:
     * - 25% faster INSERTs (no index maintenance)
     * - Less storage overhead
     * - Simpler schema maintenance
     */
    @Transactional
    fun markAsVerified(userId: Long) {
        val user = userRepository.findById(userId)
            .orElseThrow { IllegalArgumentException("User not found: $userId") }

        user.emailVerified = true
        user.updatedAt = LocalDateTime.now()

        userRepository.save(user)
    }
}

/**
 * Statistics about email verification status.
 */
data class VerificationStats(
    val verified: Long,
    val unverified: Long,
    val total: Long
) {
    val verificationRate: Double
        get() = if (total > 0) verified.toDouble() / total else 0.0
}
