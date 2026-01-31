package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

@Service
@Transactional
class PointsCalculationService(
    private val customerRepository: CustomerRepository,
    private val orderRepository: OrderRepository,
    private val pointTransactionRepository: PointTransactionRepository
) {

    fun calculateAndAwardPoints(customerId: Long, order: OrderDetails): PointsResult {
        val customer = customerRepository.findById(customerId)
            .orElseThrow { IllegalArgumentException("Customer not found: $customerId") }

        val pointsEarned = calculatePoints(order)

        if (pointsEarned > 0) {
            awardPoints(customer, order.orderId, pointsEarned)
        }

        return PointsResult(
            customerId = customerId,
            orderId = order.orderId,
            pointsEarned = pointsEarned,
            totalPoints = customer.totalPoints
        )
    }

    private fun calculatePoints(order: OrderDetails): Int {
        val baseAmount = order.subtotal

        // Calculate points based on order amount
        val points = baseAmount
            .divide(BigDecimal(POINTS_PER_YEN), 0, RoundingMode.DOWN)
            .toInt()

        return minOf(points, MAX_POINTS_PER_TRANSACTION)
    }

    private fun awardPoints(customer: Customer, orderId: Long, points: Int) {
        customer.totalPoints += points

        val transaction = PointTransaction(
            customerId = customer.id,
            orderId = orderId,
            points = points,
            transactionType = PointTransactionType.EARNED
        )
        pointTransactionRepository.save(transaction)
        customerRepository.save(customer)
    }

    fun getCustomerPoints(customerId: Long): Long {
        return customerRepository.findById(customerId)
            .map { it.totalPoints }
            .orElse(0L)
    }

    companion object {
        const val POINTS_PER_YEN = 100
        const val MAX_POINTS_PER_TRANSACTION = 10000
    }
}

data class OrderDetails(
    val orderId: Long,
    val subtotal: BigDecimal,
    val discountAmount: BigDecimal,
    val finalAmount: BigDecimal
)

data class PointsResult(
    val customerId: Long,
    val orderId: Long,
    val pointsEarned: Int,
    val totalPoints: Long
)

data class Customer(
    val id: Long = 0,
    val email: String,
    val membershipType: MembershipType,
    var totalPoints: Long = 0
)

enum class MembershipType {
    GUEST, MEMBER, PREMIUM
}

data class PointTransaction(
    val id: Long = 0,
    val customerId: Long,
    val orderId: Long?,
    val points: Int,
    val transactionType: PointTransactionType,
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class PointTransactionType {
    EARNED, REDEEMED, EXPIRED, ADJUSTED
}

interface CustomerRepository {
    fun findById(id: Long): java.util.Optional<Customer>
    fun save(customer: Customer): Customer
}

interface OrderRepository {
    fun findById(id: Long): java.util.Optional<Order>
}

interface PointTransactionRepository {
    fun save(transaction: PointTransaction): PointTransaction
}

data class Order(
    val id: Long = 0,
    val customerId: Long,
    val subtotal: BigDecimal,
    val discountAmount: BigDecimal,
    val finalAmount: BigDecimal
)
