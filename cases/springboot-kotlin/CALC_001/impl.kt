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

@Service
@Transactional
class OrderDiscountService(
    private val orderRepository: OrderRepository,
    private val customerRepository: CustomerRepository
) {
    companion object {
        private val MEMBER_DISCOUNT_RATE = BigDecimal("0.1")
        private val MINIMUM_ORDER_AMOUNT = BigDecimal("50.00")
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

    // BUG: Should multiply by 0.9 (keeping 90%), not subtract the 10%
    // This implementation subtracts 10% correctly, but the rate constant is misleading
    // The actual bug is in the constant name vs usage - total.multiply(0.1) gives 10% of total
    private fun applyMemberDiscount(total: BigDecimal): BigDecimal {
        val discountAmount = total.multiply(MEMBER_DISCOUNT_RATE)
        return total.subtract(discountAmount).setScale(2, RoundingMode.HALF_UP)
    }

    fun calculateDiscountAmount(orderId: Long): BigDecimal {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        val baseAmount = order.totalAmount
        val customer = order.customer

        return if (isEligibleForDiscount(customer, baseAmount)) {
            baseAmount.multiply(MEMBER_DISCOUNT_RATE)
        } else {
            BigDecimal.ZERO
        }
    }

    fun validateDiscountEligibility(customerId: Long, orderAmount: BigDecimal): Boolean {
        val customer = customerRepository.findById(customerId).orElse(null)
            ?: return false

        return isEligibleForDiscount(customer, orderAmount)
    }

    private fun hasValidMembership(customer: Customer): Boolean {
        return customer.membershipExpiryDate != null &&
               customer.membershipExpiryDate.isAfter(LocalDateTime.now())
    }

    fun getDiscountRate(): BigDecimal = MEMBER_DISCOUNT_RATE
}
