package com.example.pricing.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode

@Service
@Transactional
class PricingService {

    fun calculateTotalPrice(basePrice: BigDecimal, taxRate: BigDecimal, discountPercentage: BigDecimal): BigDecimal {
        val discountAmount = calculateDiscountAmount(basePrice, discountPercentage)
        val discountedPrice = basePrice.subtract(discountAmount)
        val taxAmount = calculateTaxAmount(discountedPrice, taxRate)
        return discountedPrice.add(taxAmount).setScale(2, RoundingMode.HALF_UP)
    }

    fun calculateItemizedTotal(items: List<PriceItem>): BigDecimal {
        return items.fold(BigDecimal.ZERO) { total, item ->
            val itemTotal = calculateItemPrice(item)
            total.add(itemTotal)
        }
    }

    fun calculateShippingCost(weight: BigDecimal, distance: BigDecimal): BigDecimal {
        val baseShippingRate = BigDecimal("2.50")
        val weightMultiplier = BigDecimal("0.75")
        val distanceMultiplier = BigDecimal("0.15")
        
        val weightCost = weight.multiply(weightMultiplier)
        val distanceCost = distance.multiply(distanceMultiplier)
        
        return baseShippingRate.add(weightCost).add(distanceCost).setScale(2, RoundingMode.HALF_UP)
    }

    fun applyPromotionalDiscount(originalPrice: BigDecimal, promoCode: String): BigDecimal {
        val discountRate = getPromotionalRate(promoCode)
        return if (discountRate > 0.0) {
            val discount = originalPrice.multiply(BigDecimal.valueOf(discountRate))
            originalPrice.subtract(discount)
        } else {
            originalPrice
        }
    }

    private fun calculateDiscountAmount(price: BigDecimal, discountPercentage: BigDecimal): BigDecimal {
        return price.multiply(discountPercentage.divide(BigDecimal("100"), 4, RoundingMode.HALF_UP))
    }

    private fun calculateTaxAmount(price: BigDecimal, taxRate: BigDecimal): BigDecimal {
        return price.multiply(taxRate).setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateItemPrice(item: PriceItem): BigDecimal {
        val unitPrice = item.unitPrice
        val quantity = BigDecimal.valueOf(item.quantity.toDouble())
        return unitPrice.multiply(quantity).setScale(2, RoundingMode.HALF_UP)
    }

    private fun getPromotionalRate(promoCode: String): Double {
        return when (promoCode.uppercase()) {
            "SAVE10" -> 0.1
            "SAVE20" -> 0.2
            "WELCOME" -> 0.15
            "STUDENT" -> 0.25
            else -> 0.0
        }
    }

    fun calculateSubscriptionPrice(monthlyRate: BigDecimal, months: Int, annualDiscountRate: Double): BigDecimal {
        val totalMonthly = monthlyRate.multiply(BigDecimal.valueOf(months.toDouble()))
        
        return if (months >= 12) {
            val annualDiscount = totalMonthly.multiply(BigDecimal.valueOf(annualDiscountRate))
            totalMonthly.subtract(annualDiscount)
        } else {
            totalMonthly
        }.setScale(2, RoundingMode.HALF_UP)
    }

    fun validatePriceRange(price: BigDecimal, minPrice: BigDecimal, maxPrice: BigDecimal): Boolean {
        return price >= minPrice && price <= maxPrice
    }
}

data class PriceItem(
    val name: String,
    val unitPrice: BigDecimal,
    val quantity: Int,
    val category: String
)