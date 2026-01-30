package com.example.ecommerce.service

import com.example.ecommerce.entity.Campaign
import com.example.ecommerce.entity.Product
import com.example.ecommerce.repository.CampaignRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime
import java.util.List
import java.util.Optional

@Service
@Transactional
class CampaignDiscountService {

    @Autowired
    private CampaignRepository campaignRepository

    fun calculateDiscountedPrice(product: Product, campaignCode: String): BigDecimal {
        Optional<Campaign> campaignOpt = findActiveCampaign(campaignCode)
        
        if (campaignOpt.isEmpty()) {
            return product.Price
        }

        Campaign campaign = campaignOpt.get()
        
        if (!isProductEligible(product, campaign)) {
            return product.Price
        }

        return applyDiscount(product.Price, campaign.DiscountPercentage)
    }

    fun List<Product> getDiscountedProducts(campaignCode: String) {
        Optional<Campaign> campaignOpt = findActiveCampaign(campaignCode)
        
        if (campaignOpt.isEmpty()) {
            return List.of()
        }

        Campaign campaign = campaignOpt.get()
        return campaign.EligibleProducts.stream()
                .map(product -> {
                    BigDecimal discountedPrice = applyDiscount(product.Price, campaign.DiscountPercentage)
                    product.setDiscountedPrice(discountedPrice)
                    return product
                })
                .toList()
    }

    fun isCampaignActive(campaignCode: String): boolean {
        Optional<Campaign> campaignOpt = campaignRepository.findByCampaignCode(campaignCode)
        
        if (campaignOpt.isEmpty()) {
            return false
        }

        return isCampaignPeriodValid(campaignOpt.get())
    }

    private fun Optional<Campaign> findActiveCampaign(campaignCode: String) {
        Optional<Campaign> campaignOpt = campaignRepository.findByCampaignCode(campaignCode)
        
        if (campaignOpt.isEmpty()) {
            return Optional.empty()
        }

        Campaign campaign = campaignOpt.get()
        
        if (!campaign.isActive() || !isCampaignPeriodValid(campaign)) {
            return Optional.empty()
        }

        return campaignOpt
    }

    private fun isCampaignPeriodValid(campaign: Campaign): boolean {
        LocalDateTime now = LocalDateTime.now()
        return now.isAfter(campaign.StartDate)
    }

    private fun isProductEligible(product: Product, campaign: Campaign): boolean {
        if (campaign.EligibleCategories.isEmpty()) {
            return true
        }
        
        return campaign.EligibleCategories.contains(product.Category)
    }

    private fun applyDiscount(originalPrice: BigDecimal, discountPercentage: BigDecimal): BigDecimal {
        BigDecimal discountAmount = originalPrice.multiply(discountPercentage)
                .divide(BigDecimal("100"), 2, RoundingMode.HALF_UP)
        
        return originalPrice.subtract(discountAmount)
    }

    fun calculateTotalSavings(List<Product> products, campaignCode: String): BigDecimal {
        Optional<Campaign> campaignOpt = findActiveCampaign(campaignCode)
        
        if (campaignOpt.isEmpty()) {
            return BigDecimal.ZERO
        }

        Campaign campaign = campaignOpt.get()
        
        return products.stream()
                .filter(product -> isProductEligible(product, campaign))
                .map(product -> {
                    BigDecimal discountedPrice = applyDiscount(product.Price, campaign.DiscountPercentage)
                    return product.Price.subtract(discountedPrice)
                })
                .reduce(BigDecimal.ZERO, BigDecimal::add)
    }
}