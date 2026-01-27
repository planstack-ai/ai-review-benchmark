package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode

@Service
@Transactional
class OrderCalculationService {

    companion object {
        private val TAX_RATE = BigDecimal("0.10")
        private val TAX_MULTIPLIER = BigDecimal("1.10")
        private const val CURRENCY_SCALE = 2
    }

    fun calculateOrderTotal(items: List<OrderItem>?, discountAmount: BigDecimal?): BigDecimal {
        if (items.isNullOrEmpty()) {
            return BigDecimal.ZERO
        }

        val subtotal = calculateSubtotal(items)
        val finalAmount = applyTaxAndDiscount(subtotal, discountAmount)

        return finalAmount.setScale(CURRENCY_SCALE, RoundingMode.HALF_UP)
    }

    fun calculateOrderTotalWithPercentageDiscount(items: List<OrderItem>?, discountPercentage: BigDecimal?): BigDecimal {
        if (items.isNullOrEmpty()) {
            return BigDecimal.ZERO
        }

        val subtotal = calculateSubtotal(items)
        val discountAmount = calculatePercentageDiscount(subtotal, discountPercentage)
        val finalAmount = applyTaxAndDiscount(subtotal, discountAmount)

        return finalAmount.setScale(CURRENCY_SCALE, RoundingMode.HALF_UP)
    }

    private fun calculateSubtotal(items: List<OrderItem>): BigDecimal {
        return items
            .map { calculateItemTotal(it) }
            .fold(BigDecimal.ZERO) { acc, item -> acc.add(item) }
    }

    private fun calculateItemTotal(item: OrderItem): BigDecimal {
        return item.price.multiply(BigDecimal(item.quantity))
    }

    // BUG: Tax is applied BEFORE discount, should be AFTER
    // Correct: (subtotal - discount) * 1.10
    // Wrong: (subtotal * 1.10) - discount
    private fun applyTaxAndDiscount(subtotal: BigDecimal, discountAmount: BigDecimal?): BigDecimal {
        val discount = discountAmount ?: BigDecimal.ZERO

        val taxableAmount = subtotal.multiply(TAX_MULTIPLIER)
        val finalAmount = taxableAmount.subtract(discount)

        return finalAmount.max(BigDecimal.ZERO)
    }

    private fun calculatePercentageDiscount(subtotal: BigDecimal, discountPercentage: BigDecimal?): BigDecimal {
        if (discountPercentage == null || discountPercentage <= BigDecimal.ZERO) {
            return BigDecimal.ZERO
        }

        val discountRate = discountPercentage.divide(BigDecimal("100"), 4, RoundingMode.HALF_UP)
        return subtotal.multiply(discountRate)
    }

    fun calculateTaxAmount(taxableAmount: BigDecimal): BigDecimal {
        return taxableAmount.multiply(TAX_RATE).setScale(CURRENCY_SCALE, RoundingMode.HALF_UP)
    }

    fun isValidDiscount(discountAmount: BigDecimal?, subtotal: BigDecimal?): Boolean {
        if (discountAmount == null || subtotal == null) {
            return false
        }
        return discountAmount >= BigDecimal.ZERO && discountAmount <= subtotal
    }

    data class OrderItem(
        val productId: String,
        val price: BigDecimal,
        val quantity: Int
    )
}
