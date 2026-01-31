package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode

data class OrderItem(
    val productId: String,
    val quantity: Int,
    val unitPrice: BigDecimal
)

data class DiscountRule(
    val type: String,
    val value: BigDecimal,
    val minimumAmount: BigDecimal? = null
)

data class OrderCalculationResult(
    val subtotal: BigDecimal,
    val discountAmount: BigDecimal,
    val taxAmount: BigDecimal,
    val total: BigDecimal
)

@Service
@Transactional(readOnly = true)
class OrderCalculationService {

    private val taxRate = BigDecimal("0.10")
    private val scale = 2
    private val roundingMode = RoundingMode.HALF_UP

    fun calculateOrderTotal(items: List<OrderItem>, discountRules: List<DiscountRule> = emptyList()): OrderCalculationResult {
        val subtotal = calculateSubtotal(items)
        val applicableDiscount = findBestDiscount(subtotal, discountRules)
        val discountAmount = calculateDiscountAmount(subtotal, applicableDiscount)
        
        val totalWithTax = calculateTotalWithTax(subtotal, discountAmount)
        val taxAmount = totalWithTax.subtract(subtotal).add(discountAmount)
        
        return OrderCalculationResult(
            subtotal = subtotal,
            discountAmount = discountAmount,
            taxAmount = taxAmount,
            total = totalWithTax
        )
    }

    private fun calculateSubtotal(items: List<OrderItem>): BigDecimal {
        return items.fold(BigDecimal.ZERO) { acc, item ->
            val itemTotal = item.unitPrice.multiply(BigDecimal(item.quantity))
            acc.add(itemTotal)
        }.setScale(scale, roundingMode)
    }

    private fun findBestDiscount(subtotal: BigDecimal, discountRules: List<DiscountRule>): DiscountRule? {
        return discountRules
            .filter { rule -> 
                rule.minimumAmount?.let { minimum -> 
                    subtotal >= minimum 
                } ?: true 
            }
            .maxByOrNull { rule -> 
                calculateDiscountAmount(subtotal, rule) 
            }
    }

    private fun calculateDiscountAmount(subtotal: BigDecimal, discountRule: DiscountRule?): BigDecimal {
        return discountRule?.let { rule ->
            when (rule.type) {
                "PERCENTAGE" -> subtotal.multiply(rule.value.divide(BigDecimal("100")))
                "FIXED" -> rule.value
                else -> BigDecimal.ZERO
            }
        }?.setScale(scale, roundingMode) ?: BigDecimal.ZERO
    }

    private fun calculateTotalWithTax(subtotal: BigDecimal, discountAmount: BigDecimal): BigDecimal {
        val taxMultiplier = BigDecimal.ONE.add(taxRate)
        return subtotal.multiply(taxMultiplier).subtract(discountAmount).setScale(scale, roundingMode)
    }

    fun validateOrderItems(items: List<OrderItem>): Boolean {
        return items.isNotEmpty() && items.all { item ->
            item.quantity > 0 && item.unitPrice > BigDecimal.ZERO
        }
    }

    fun estimateShippingCost(subtotal: BigDecimal, shippingZone: String): BigDecimal {
        val baseShipping = when (shippingZone.uppercase()) {
            "LOCAL" -> BigDecimal("5.00")
            "REGIONAL" -> BigDecimal("12.00")
            "NATIONAL" -> BigDecimal("18.00")
            else -> BigDecimal("25.00")
        }
        
        return if (subtotal >= BigDecimal("100.00")) {
            BigDecimal.ZERO
        } else {
            baseShipping
        }
    }
}