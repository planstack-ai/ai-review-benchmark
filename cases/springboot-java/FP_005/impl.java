package com.example.pricing.service;

import com.example.pricing.entity.Product;
import com.example.pricing.entity.PriceAdjustment;
import com.example.pricing.entity.AdjustmentType;
import com.example.pricing.repository.ProductRepository;
import com.example.pricing.repository.PriceAdjustmentRepository;
import com.example.pricing.constants.PricingConstants;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Service
@Transactional(readOnly = true)
public class PricingServiceImpl implements PricingService {

    private final ProductRepository productRepository;
    private final PriceAdjustmentRepository priceAdjustmentRepository;

    @Autowired
    public PricingServiceImpl(ProductRepository productRepository, 
                             PriceAdjustmentRepository priceAdjustmentRepository) {
        this.productRepository = productRepository;
        this.priceAdjustmentRepository = priceAdjustmentRepository;
    }

    @Override
    public BigDecimal calculateFinalPrice(Long productId, LocalDate effectiveDate) {
        Optional<Product> productOpt = productRepository.findById(productId);
        if (!productOpt.isPresent()) {
            throw new IllegalArgumentException("Product not found with id: " + productId);
        }

        Product product = productOpt.get();
        BigDecimal basePrice = product.getBasePrice();
        
        List<PriceAdjustment> adjustments = priceAdjustmentRepository
            .findByProductIdAndEffectiveDateLessThanEqual(productId, effectiveDate);
        
        BigDecimal adjustedPrice = applyPriceAdjustments(basePrice, adjustments);
        
        return adjustedPrice.setScale(PricingConstants.PRICE_SCALE, PricingConstants.PRICE_ROUNDING);
    }

    @Override
    public BigDecimal applyTax(BigDecimal price) {
        if (price == null || price.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Price cannot be null or negative");
        }
        
        BigDecimal taxAmount = price.multiply(PricingConstants.TAX_RATE);
        BigDecimal totalWithTax = price.add(taxAmount);
        
        return totalWithTax.setScale(PricingConstants.PRICE_SCALE, PricingConstants.PRICE_ROUNDING);
    }

    @Override
    public BigDecimal calculateDiscount(BigDecimal basePrice, BigDecimal discountPercentage) {
        if (basePrice == null || discountPercentage == null) {
            throw new IllegalArgumentException("Base price and discount percentage cannot be null");
        }
        
        if (discountPercentage.compareTo(PricingConstants.MAX_DISCOUNT_PERCENTAGE) > 0) {
            discountPercentage = PricingConstants.MAX_DISCOUNT_PERCENTAGE;
        }
        
        BigDecimal discountAmount = basePrice.multiply(discountPercentage);
        return discountAmount.setScale(PricingConstants.PRICE_SCALE, PricingConstants.PRICE_ROUNDING);
    }

    private BigDecimal applyPriceAdjustments(BigDecimal basePrice, List<PriceAdjustment> adjustments) {
        BigDecimal currentPrice = basePrice;
        
        for (PriceAdjustment adjustment : adjustments) {
            currentPrice = applyIndividualAdjustment(currentPrice, adjustment);
        }
        
        return currentPrice;
    }

    private BigDecimal applyIndividualAdjustment(BigDecimal currentPrice, PriceAdjustment adjustment) {
        BigDecimal adjustmentValue = adjustment.getAdjustmentValue();
        AdjustmentType adjustmentType = adjustment.getAdjustmentType();
        
        switch (adjustmentType) {
            case DISCOUNT:
                BigDecimal discountAmount = calculateDiscount(currentPrice, adjustmentValue);
                return currentPrice.subtract(discountAmount);
            case MARKUP:
                BigDecimal markupAmount = currentPrice.multiply(adjustmentValue);
                return currentPrice.add(markupAmount);
            case SEASONAL:
                return currentPrice.add(adjustmentValue);
            default:
                return currentPrice;
        }
    }
}