package com.example.service

import com.example.entity.Customer
import com.example.entity.Order
import com.example.entity.MembershipType
import com.example.repository.CustomerRepository
import com.example.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal

/**
 * This is a CORRECTLY implemented order service.
 * No bugs - should NOT trigger any critical or major issues.
 */
@Service
@Transactional
class OrderService(
    private val customerRepository: CustomerRepository,
    private val orderRepository: OrderRepository,
    private val pricingService: PricingService
) {

    fun createOrder(customerEmail: String, subtotal: BigDecimal): Order {
        validateSubtotal(subtotal)
        val customer = findCustomerByEmail(customerEmail)

        val discountAmount = calculateDiscountForCustomer(customer, subtotal)
        val totalAmount = pricingService.calculateTotalWithDiscount(subtotal, discountAmount)

        val order = buildOrder(customer, subtotal, discountAmount, totalAmount)

        return orderRepository.save(order)
    }

    fun getCustomerOrderHistory(customerEmail: String): List<Order> {
        val customer = findCustomerByEmail(customerEmail)
        val customerId = customer.id
            ?: throw IllegalStateException("Customer ID is null")
        return orderRepository.findByCustomerIdOrderByCreatedAtDesc(customerId)
    }

    fun calculateOrderTotal(customerEmail: String, subtotal: BigDecimal): BigDecimal {
        validateSubtotal(subtotal)
        val customer = findCustomerByEmail(customerEmail)
        val discountAmount = calculateDiscountForCustomer(customer, subtotal)
        return pricingService.calculateTotalWithDiscount(subtotal, discountAmount)
    }

    private fun findCustomerByEmail(email: String): Customer {
        return customerRepository.findByEmail(email)
            .orElseThrow { IllegalArgumentException("Customer not found with email: $email") }
    }

    private fun calculateDiscountForCustomer(customer: Customer, subtotal: BigDecimal): BigDecimal {
        return if (isEligibleForMemberDiscount(customer)) {
            pricingService.calculateMemberDiscount(subtotal)
        } else {
            BigDecimal.ZERO
        }
    }

    private fun isEligibleForMemberDiscount(customer: Customer): Boolean {
        val membershipType = customer.membershipType
        return membershipType == MembershipType.PREMIUM || membershipType == MembershipType.VIP
    }

    private fun buildOrder(
        customer: Customer,
        subtotal: BigDecimal,
        discountAmount: BigDecimal,
        totalAmount: BigDecimal
    ): Order {
        return Order().apply {
            this.customer = customer
            this.subtotal = subtotal
            this.discountAmount = discountAmount
            this.totalAmount = totalAmount
        }
    }

    private fun validateSubtotal(subtotal: BigDecimal) {
        if (subtotal.compareTo(BigDecimal.ZERO) <= 0) {
            throw IllegalArgumentException("Subtotal must be positive")
        }
    }
}
