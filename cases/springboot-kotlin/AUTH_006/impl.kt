package com.example.service

import org.springframework.data.domain.Page
import org.springframework.data.domain.PageRequest
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional(readOnly = true)
class PointsService(
    private val userRepository: UserRepository,
    private val pointTransactionRepository: PointTransactionRepository
) {

    fun getUserPoints(userId: Long): PointsBalanceResponse {
        val user = userRepository.findById(userId)
            .orElseThrow { IllegalArgumentException("User not found: $userId") }

        val recentTransactions = pointTransactionRepository
            .findByUserIdOrderByCreatedAtDesc(userId, PageRequest.of(0, 10))

        return PointsBalanceResponse(
            userId = user.id,
            totalPoints = user.totalPoints,
            recentTransactions = recentTransactions.content.map { it.toDto() }
        )
    }

    fun getPointsHistory(userId: Long, page: Int, size: Int): Page<PointTransactionDto> {
        val pageable = PageRequest.of(page, size)
        return pointTransactionRepository
            .findByUserIdOrderByCreatedAtDesc(userId, pageable)
            .map { it.toDto() }
    }

    private fun PointTransaction.toDto() = PointTransactionDto(
        id = this.id,
        points = this.points,
        transactionType = this.transactionType,
        description = this.description,
        createdAt = this.createdAt
    )
}

data class PointsBalanceResponse(
    val userId: Long,
    val totalPoints: Long,
    val recentTransactions: List<PointTransactionDto>
)

data class PointTransactionDto(
    val id: Long,
    val points: Int,
    val transactionType: TransactionType,
    val description: String?,
    val createdAt: LocalDateTime
)

data class User(
    val id: Long = 0,
    val email: String,
    var totalPoints: Long = 0
)

data class PointTransaction(
    val id: Long = 0,
    val userId: Long,
    val points: Int,
    val transactionType: TransactionType,
    val description: String?,
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class TransactionType {
    EARNED, REDEEMED, EXPIRED, BONUS
}

interface UserRepository {
    fun findById(id: Long): java.util.Optional<User>
}

interface PointTransactionRepository {
    fun findByUserIdOrderByCreatedAtDesc(userId: Long, pageable: PageRequest): Page<PointTransaction>
}

data class Page<T>(
    val content: List<T>,
    val totalElements: Long,
    val totalPages: Int
) {
    fun <R> map(transform: (T) -> R): Page<R> = Page(content.map(transform), totalElements, totalPages)
}

data class PageRequest(val page: Int, val size: Int) {
    companion object {
        fun of(page: Int, size: Int) = PageRequest(page, size)
    }
}

data class UserPrincipal(
    val id: Long,
    val email: String
)
