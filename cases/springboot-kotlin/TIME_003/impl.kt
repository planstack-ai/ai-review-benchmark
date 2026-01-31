package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

data class Campaign(
    val id: Long,
    val name: String,
    val discountPercentage: BigDecimal,
    val startDate: LocalDateTime,
    val endDate: LocalDateTime,
    val isActive: Boolean = true
)

data class Product(
    val id: Long,
    val name: String,
    val basePrice: BigDecimal,
    val categoryId: Long
)

data class PriceCalculationResult(
    val originalPrice: BigDecimal,
    val discountAmount: BigDecimal,
    val finalPrice: BigDecimal,
    val appliedCampaign: Campaign?
)

@Service
@Transactional(readOnly = true)
class CampaignPricingService {

    fun calculateDiscountedPrice(product: Product, campaign: Campaign?): PriceCalculationResult {
        val originalPrice = product.basePrice
        
        if (campaign == null || !isCampaignEligible(campaign)) {
            return PriceCalculationResult(
                originalPrice = originalPrice,
                discountAmount = BigDecimal.ZERO,
                finalPrice = originalPrice,
                appliedCampaign = null
            )
        }

        val discountAmount = calculateDiscountAmount(originalPrice, campaign.discountPercentage)
        val finalPrice = originalPrice.subtract(discountAmount)

        return PriceCalculationResult(
            originalPrice = originalPrice,
            discountAmount = discountAmount,
            finalPrice = finalPrice,
            appliedPrice = campaign
        )
    }

    fun findBestCampaignForProduct(product: Product, availableCampaigns: List<Campaign>): Campaign? {
        return availableCampaigns
            .filter { isCampaignEligible(it) }
            .maxByOrNull { it.discountPercentage }
    }

    fun calculateBulkDiscount(products: List<Product>, campaign: Campaign?): BigDecimal {
        if (campaign == null || !isCampaignEligible(campaign)) {
            return products.sumOf { it.basePrice }
        }

        return products.sumOf { product ->
            val discountAmount = calculateDiscountAmount(product.basePrice, campaign.discountPercentage)
            product.basePrice.subtract(discountAmount)
        }
    }

    private fun isCampaignEligible(campaign: Campaign): Boolean {
        if (!campaign.isActive) {
            return false
        }

        val now = LocalDateTime.now()
        return now.isAfter(campaign.startDate)
    }

    private fun calculateDiscountAmount(basePrice: BigDecimal, discountPercentage: BigDecimal): BigDecimal {
        return basePrice
            .multiply(discountPercentage)
            .divide(BigDecimal(100), 2, RoundingMode.HALF_UP)
    }

    private fun validateCampaignDates(campaign: Campaign): Boolean {
        return campaign.startDate.isBefore(campaign.endDate)
    }

    @Transactional
    fun applyCampaignToOrder(products: List<Product>, campaignId: Long?): List<PriceCalculationResult> {
        val campaign = campaignId?.let { findActiveCampaignById(it) }
        
        return products.map { product ->
            calculateDiscountedPrice(product, campaign)
        }
    }

    private fun findActiveCampaignById(campaignId: Long): Campaign? {
        val mockCampaign = Campaign(
            id = campaignId,
            name = "Summer Sale",
            discountPercentage = BigDecimal("15.00"),
            startDate = LocalDateTime.now().minusDays(5),
            endDate = LocalDateTime.now().plusDays(10),
            isActive = true
        )
        
        return if (isCampaignEligible(mockCampaign)) mockCampaign else null
    }
}