package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

@Service
@Transactional
class CouponApplicationService(
    private val couponRepository: CouponRepository,
    private val orderRepository: OrderRepository
) {

    fun applyCoupon(orderId: Long, couponCode: String): CouponApplicationResult {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val coupon = couponRepository.findByCode(couponCode)
            ?: throw CouponException("Invalid coupon code: $couponCode")

        validateCoupon(coupon, order)

        val discountAmount = calculateDiscount(coupon, order.subtotal)

        order.couponId = coupon.id
        order.couponDiscount = discountAmount
        order.finalAmount = order.subtotal.subtract(discountAmount)

        if (coupon.isSingleUse) {
            coupon.isUsed = true
            couponRepository.save(coupon)
        }

        orderRepository.save(order)

        return CouponApplicationResult(
            orderId = orderId,
            couponCode = couponCode,
            discountAmount = discountAmount,
            finalAmount = order.finalAmount,
            success = true
        )
    }

    private fun validateCoupon(coupon: Coupon, order: Order) {
        if (coupon.expiresAt != null && coupon.expiresAt.isBefore(LocalDateTime.now())) {
            throw CouponExpiredException("Coupon has expired: ${coupon.code}")
        }

        if (coupon.isSingleUse && coupon.isUsed) {
            throw CouponAlreadyUsedException("Coupon already used: ${coupon.code}")
        }

        if (order.subtotal < coupon.minimumOrderAmount) {
            throw MinimumOrderAmountException(
                "Order amount ${order.subtotal} is below minimum ${coupon.minimumOrderAmount}"
            )
        }
    }

    private fun calculateDiscount(coupon: Coupon, subtotal: BigDecimal): BigDecimal {
        val discount = when (coupon.discountType) {
            DiscountType.PERCENTAGE -> subtotal.multiply(coupon.discountValue)
                .divide(BigDecimal(100), 2, RoundingMode.HALF_UP)
            DiscountType.FIXED_AMOUNT -> coupon.discountValue
        }

        return minOf(discount, subtotal)
    }

    fun removeCoupon(orderId: Long): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        order.couponId = null
        order.couponDiscount = BigDecimal.ZERO
        order.finalAmount = order.subtotal

        return orderRepository.save(order)
    }
}

data class CouponApplicationResult(
    val orderId: Long,
    val couponCode: String,
    val discountAmount: BigDecimal,
    val finalAmount: BigDecimal,
    val success: Boolean
)

data class Coupon(
    val id: Long = 0,
    val code: String,
    val discountType: DiscountType,
    val discountValue: BigDecimal,
    val minimumOrderAmount: BigDecimal = BigDecimal.ZERO,
    val expiresAt: LocalDateTime?,
    val isSingleUse: Boolean = false,
    var isUsed: Boolean = false
)

enum class DiscountType {
    PERCENTAGE, FIXED_AMOUNT
}

data class Order(
    val id: Long = 0,
    val customerId: Long,
    val subtotal: BigDecimal,
    var couponId: Long? = null,
    var couponDiscount: BigDecimal = BigDecimal.ZERO,
    var finalAmount: BigDecimal,
    var status: OrderStatus
)

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

interface CouponRepository {
    fun findById(id: Long): java.util.Optional<Coupon>
    fun findByCode(code: String): Coupon?
    fun save(coupon: Coupon): Coupon
}

interface OrderRepository {
    fun findById(id: Long): java.util.Optional<Order>
    fun save(order: Order): Order
}

open class CouponException(message: String) : RuntimeException(message)
class CouponExpiredException(message: String) : CouponException(message)
class CouponAlreadyUsedException(message: String) : CouponException(message)
class MinimumOrderAmountException(message: String) : CouponException(message)
