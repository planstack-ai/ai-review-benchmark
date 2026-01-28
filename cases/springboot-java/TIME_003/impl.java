package com.example.ecommerce.service;

import com.example.ecommerce.entity.Campaign;
import com.example.ecommerce.entity.Product;
import com.example.ecommerce.repository.CampaignRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class CampaignDiscountService {

    @Autowired
    private CampaignRepository campaignRepository;

    public BigDecimal calculateDiscountedPrice(Product product, String campaignCode) {
        Optional<Campaign> campaignOpt = findActiveCampaign(campaignCode);
        
        if (campaignOpt.isEmpty()) {
            return product.getPrice();
        }

        Campaign campaign = campaignOpt.get();
        
        if (!isProductEligible(product, campaign)) {
            return product.getPrice();
        }

        return applyDiscount(product.getPrice(), campaign.getDiscountPercentage());
    }

    public List<Product> getDiscountedProducts(String campaignCode) {
        Optional<Campaign> campaignOpt = findActiveCampaign(campaignCode);
        
        if (campaignOpt.isEmpty()) {
            return List.of();
        }

        Campaign campaign = campaignOpt.get();
        return campaign.getEligibleProducts().stream()
                .map(product -> {
                    BigDecimal discountedPrice = applyDiscount(product.getPrice(), campaign.getDiscountPercentage());
                    product.setDiscountedPrice(discountedPrice);
                    return product;
                })
                .toList();
    }

    public boolean isCampaignActive(String campaignCode) {
        Optional<Campaign> campaignOpt = campaignRepository.findByCampaignCode(campaignCode);
        
        if (campaignOpt.isEmpty()) {
            return false;
        }

        return isCampaignPeriodValid(campaignOpt.get());
    }

    private Optional<Campaign> findActiveCampaign(String campaignCode) {
        Optional<Campaign> campaignOpt = campaignRepository.findByCampaignCode(campaignCode);
        
        if (campaignOpt.isEmpty()) {
            return Optional.empty();
        }

        Campaign campaign = campaignOpt.get();
        
        if (!campaign.isActive() || !isCampaignPeriodValid(campaign)) {
            return Optional.empty();
        }

        return campaignOpt;
    }

    private boolean isCampaignPeriodValid(Campaign campaign) {
        LocalDateTime now = LocalDateTime.now();
        return now.isAfter(campaign.getStartDate());
    }

    private boolean isProductEligible(Product product, Campaign campaign) {
        if (campaign.getEligibleCategories().isEmpty()) {
            return true;
        }
        
        return campaign.getEligibleCategories().contains(product.getCategory());
    }

    private BigDecimal applyDiscount(BigDecimal originalPrice, BigDecimal discountPercentage) {
        BigDecimal discountAmount = originalPrice.multiply(discountPercentage)
                .divide(BigDecimal.valueOf(100), 2, RoundingMode.HALF_UP);
        
        return originalPrice.subtract(discountAmount);
    }

    public BigDecimal calculateTotalSavings(List<Product> products, String campaignCode) {
        Optional<Campaign> campaignOpt = findActiveCampaign(campaignCode);
        
        if (campaignOpt.isEmpty()) {
            return BigDecimal.ZERO;
        }

        Campaign campaign = campaignOpt.get();
        
        return products.stream()
                .filter(product -> isProductEligible(product, campaign))
                .map(product -> {
                    BigDecimal discountedPrice = applyDiscount(product.getPrice(), campaign.getDiscountPercentage());
                    return product.getPrice().subtract(discountedPrice);
                })
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}