package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

@Service
@Transactional
class CouponRedemptionService(
    private val userCouponRepository: UserCouponRepository,
    private val orderRepository: OrderRepository
) {

    fun redeemCoupon(couponCode: String, orderId: Long): CouponRedemptionResult {
        val coupon = userCouponRepository.findByCode(couponCode)
            ?: throw CouponNotFoundException("Coupon not found: $couponCode")

        validateCoupon(coupon)

        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val discountAmount = calculateDiscount(coupon, order.subtotal)

        order.couponId = coupon.id
        order.discountAmount = discountAmount
        order.finalAmount = order.subtotal.subtract(discountAmount)

        coupon.isUsed = true
        coupon.usedAt = LocalDateTime.now()

        userCouponRepository.save(coupon)
        orderRepository.save(order)

        return CouponRedemptionResult(
            success = true,
            couponCode = couponCode,
            discountAmount = discountAmount,
            finalAmount = order.finalAmount
        )
    }

    private fun validateCoupon(coupon: UserCoupon) {
        if (coupon.isUsed) {
            throw CouponAlreadyUsedException("Coupon already used: ${coupon.code}")
        }

        if (coupon.expiresAt != null && coupon.expiresAt.isBefore(LocalDateTime.now())) {
            throw CouponExpiredException("Coupon expired: ${coupon.code}")
        }
    }

    private fun calculateDiscount(coupon: UserCoupon, subtotal: BigDecimal): BigDecimal {
        return when (coupon.discountType) {
            DiscountType.PERCENTAGE -> subtotal.multiply(coupon.discountValue)
                .divide(BigDecimal(100), 2, RoundingMode.HALF_UP)
            DiscountType.FIXED_AMOUNT -> minOf(coupon.discountValue, subtotal)
        }
    }

    fun getAvailableCoupons(userId: Long): List<UserCoupon> {
        return userCouponRepository.findByUserIdAndIsUsedFalse(userId)
            .filter { it.expiresAt == null || it.expiresAt.isAfter(LocalDateTime.now()) }
    }
}

data class CouponRedemptionResult(
    val success: Boolean,
    val couponCode: String,
    val discountAmount: BigDecimal,
    val finalAmount: BigDecimal
)

data class UserCoupon(
    val id: Long = 0,
    val userId: Long,
    val code: String,
    val discountType: DiscountType,
    val discountValue: BigDecimal,
    val expiresAt: LocalDateTime?,
    var isUsed: Boolean = false,
    var usedAt: LocalDateTime? = null
)

enum class DiscountType {
    PERCENTAGE, FIXED_AMOUNT
}

data class Order(
    val id: Long = 0,
    val userId: Long,
    val subtotal: BigDecimal,
    var couponId: Long? = null,
    var discountAmount: BigDecimal = BigDecimal.ZERO,
    var finalAmount: BigDecimal
)

interface UserCouponRepository {
    fun findByCode(code: String): UserCoupon?
    fun findByCodeAndUserId(code: String, userId: Long): UserCoupon?
    fun findByUserIdAndIsUsedFalse(userId: Long): List<UserCoupon>
    fun save(coupon: UserCoupon): UserCoupon
}

interface OrderRepository {
    fun findById(id: Long): java.util.Optional<Order>
    fun save(order: Order): Order
}

class CouponNotFoundException(message: String) : RuntimeException(message)
class CouponExpiredException(message: String) : RuntimeException(message)
class CouponAlreadyUsedException(message: String) : RuntimeException(message)
