package com.example.pricing.service

import com.example.pricing.entity.Product
import com.example.pricing.entity.PriceAdjustment
import com.example.pricing.entity.AdjustmentType
import com.example.pricing.repository.ProductRepository
import com.example.pricing.repository.PriceAdjustmentRepository
import com.example.pricing.constants.PricingConstants
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDate

/**
 * This is a CORRECTLY implemented pricing service with proper BigDecimal usage.
 * No bugs - should NOT trigger any critical or major issues.
 */
@Service
@Transactional(readOnly = true)
class PricingServiceImpl(
    private val productRepository: ProductRepository,
    private val priceAdjustmentRepository: PriceAdjustmentRepository
) : PricingService {

    override fun calculateFinalPrice(productId: Long, effectiveDate: LocalDate): BigDecimal {
        val product = productRepository.findById(productId)
            .orElseThrow { IllegalArgumentException("Product not found with id: $productId") }

        val basePrice = product.basePrice

        val adjustments = priceAdjustmentRepository
            .findByProductIdAndEffectiveDateLessThanEqual(productId, effectiveDate)

        val adjustedPrice = applyPriceAdjustments(basePrice, adjustments)

        return adjustedPrice.setScale(PricingConstants.PRICE_SCALE, PricingConstants.PRICE_ROUNDING)
    }

    override fun applyTax(price: BigDecimal): BigDecimal {
        if (price.compareTo(BigDecimal.ZERO) < 0) {
            throw IllegalArgumentException("Price cannot be negative")
        }

        val taxAmount = price.multiply(PricingConstants.TAX_RATE)
        val totalWithTax = price.add(taxAmount)

        return totalWithTax.setScale(PricingConstants.PRICE_SCALE, PricingConstants.PRICE_ROUNDING)
    }

    override fun calculateDiscount(basePrice: BigDecimal, discountPercentage: BigDecimal): BigDecimal {
        val cappedPercentage = if (discountPercentage.compareTo(PricingConstants.MAX_DISCOUNT_PERCENTAGE) > 0) {
            PricingConstants.MAX_DISCOUNT_PERCENTAGE
        } else {
            discountPercentage
        }

        val discountAmount = basePrice.multiply(cappedPercentage)
        return discountAmount.setScale(PricingConstants.PRICE_SCALE, PricingConstants.PRICE_ROUNDING)
    }

    private fun applyPriceAdjustments(basePrice: BigDecimal, adjustments: List<PriceAdjustment>): BigDecimal {
        // Sort adjustments by type to ensure correct order: DISCOUNT -> MARKUP -> SEASONAL
        val sortedAdjustments = adjustments.sortedBy { adjustment ->
            when (adjustment.adjustmentType) {
                AdjustmentType.DISCOUNT -> 0
                AdjustmentType.MARKUP -> 1
                AdjustmentType.SEASONAL -> 2
                else -> 3
            }
        }

        var currentPrice = basePrice

        for (adjustment in sortedAdjustments) {
            currentPrice = applyIndividualAdjustment(currentPrice, adjustment)
        }

        return currentPrice
    }

    private fun applyIndividualAdjustment(currentPrice: BigDecimal, adjustment: PriceAdjustment): BigDecimal {
        val adjustmentValue = adjustment.adjustmentValue
        val adjustmentType = adjustment.adjustmentType

        return when (adjustmentType) {
            AdjustmentType.DISCOUNT -> {
                val discountAmount = calculateDiscount(currentPrice, adjustmentValue)
                currentPrice.subtract(discountAmount)
            }
            AdjustmentType.MARKUP -> {
                val markupAmount = currentPrice.multiply(adjustmentValue)
                currentPrice.add(markupAmount)
            }
            AdjustmentType.SEASONAL -> {
                currentPrice.add(adjustmentValue)
            }
            else -> currentPrice
        }
    }
}
