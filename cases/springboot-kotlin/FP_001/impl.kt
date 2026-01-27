package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import com.example.model.Order
import com.example.model.Customer
import com.example.repository.OrderRepository
import com.example.repository.CustomerRepository
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

/**
 * This is a CORRECTLY implemented discount service.
 * No bugs - should NOT trigger any critical or major issues.
 */
@Service
@Transactional
class OrderDiscountService(
    private val orderRepository: OrderRepository,
    private val customerRepository: CustomerRepository
) {
    companion object {
        private val MEMBER_DISCOUNT_RATE = BigDecimal("0.10") // 10% discount
        private val MINIMUM_ORDER_AMOUNT = BigDecimal("50.00")
        private const val CURRENCY_SCALE = 2
    }

    fun calculateFinalAmount(orderId: Long): BigDecimal {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        val baseAmount = order.totalAmount
        val customer = order.customer

        return if (isEligibleForDiscount(customer, baseAmount)) {
            applyMemberDiscount(baseAmount)
        } else {
            baseAmount
        }
    }

    fun processOrderWithDiscount(orderId: Long): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        val originalAmount = order.totalAmount
        val finalAmount = calculateFinalAmount(orderId)

        order.finalAmount = finalAmount
        order.discountApplied = finalAmount < originalAmount
        order.processedAt = LocalDateTime.now()

        return orderRepository.save(order)
    }

    private fun isEligibleForDiscount(customer: Customer?, orderAmount: BigDecimal): Boolean {
        return customer != null &&
               customer.isMembershipActive &&
               orderAmount >= MINIMUM_ORDER_AMOUNT
    }

    // CORRECT: Multiplies by (1 - discount rate) = 0.9 to keep 90%
    private fun applyMemberDiscount(total: BigDecimal): BigDecimal {
        val keepRate = BigDecimal.ONE.subtract(MEMBER_DISCOUNT_RATE) // 0.9
        return total.multiply(keepRate).setScale(CURRENCY_SCALE, RoundingMode.HALF_UP)
    }

    fun calculateDiscountAmount(orderId: Long): BigDecimal {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        val baseAmount = order.totalAmount
        val customer = order.customer

        return if (isEligibleForDiscount(customer, baseAmount)) {
            baseAmount.multiply(MEMBER_DISCOUNT_RATE).setScale(CURRENCY_SCALE, RoundingMode.HALF_UP)
        } else {
            BigDecimal.ZERO
        }
    }

    fun validateDiscountEligibility(customerId: Long, orderAmount: BigDecimal): Boolean {
        val customer = customerRepository.findById(customerId).orElse(null)
            ?: return false

        return isEligibleForDiscount(customer, orderAmount)
    }

    fun getDiscountRate(): BigDecimal = MEMBER_DISCOUNT_RATE
}
