package com.example.pricing.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

@Service
@Transactional
public class PricingCalculationService {

    private static final BigDecimal TAX_RATE = new BigDecimal("0.08");
    private static final BigDecimal DISCOUNT_THRESHOLD = new BigDecimal("100.00");
    private static final BigDecimal PREMIUM_DISCOUNT = new BigDecimal("0.15");
    private static final BigDecimal STANDARD_DISCOUNT = new BigDecimal("0.10");

    public BigDecimal calculateTotalPrice(List<PriceItem> items, String customerTier) {
        BigDecimal subtotal = calculateSubtotal(items);
        BigDecimal discountAmount = calculateDiscount(subtotal, customerTier);
        BigDecimal discountedPrice = subtotal.subtract(discountAmount);
        BigDecimal taxAmount = calculateTax(discountedPrice);
        
        return discountedPrice.add(taxAmount).setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateSubtotal(List<PriceItem> items) {
        BigDecimal total = BigDecimal.ZERO;
        
        for (PriceItem item : items) {
            BigDecimal itemTotal = item.getUnitPrice().multiply(new BigDecimal(item.getQuantity()));
            total = total.add(itemTotal);
        }
        
        return total;
    }

    private BigDecimal calculateDiscount(BigDecimal subtotal, String customerTier) {
        if (subtotal.compareTo(DISCOUNT_THRESHOLD) < 0) {
            return BigDecimal.ZERO;
        }

        BigDecimal discountRate = getDiscountRate(customerTier);
        return subtotal.multiply(discountRate).setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal getDiscountRate(String customerTier) {
        if ("PREMIUM".equalsIgnoreCase(customerTier)) {
            return PREMIUM_DISCOUNT;
        } else if ("STANDARD".equalsIgnoreCase(customerTier)) {
            return STANDARD_DISCOUNT;
        }
        return BigDecimal.ZERO;
    }

    private BigDecimal calculateTax(BigDecimal amount) {
        return amount.multiply(TAX_RATE).setScale(2, RoundingMode.HALF_UP);
    }

    public Map<String, BigDecimal> calculatePriceBreakdown(List<PriceItem> items, String customerTier) {
        Map<String, BigDecimal> breakdown = new HashMap<>();
        
        BigDecimal subtotal = calculateSubtotal(items);
        BigDecimal discountAmount = calculateDiscount(subtotal, customerTier);
        BigDecimal discountedPrice = subtotal.subtract(discountAmount);
        BigDecimal taxAmount = calculateTax(discountedPrice);
        BigDecimal processingFee = calculateProcessingFee(discountedPrice);
        BigDecimal total = discountedPrice.add(taxAmount).add(processingFee);
        
        breakdown.put("subtotal", subtotal);
        breakdown.put("discount", discountAmount);
        breakdown.put("tax", taxAmount);
        breakdown.put("processingFee", processingFee);
        breakdown.put("total", total);
        
        return breakdown;
    }

    private BigDecimal calculateProcessingFee(BigDecimal amount) {
        double baseRate = 0.1;
        double additionalRate = 0.2;
        double totalRate = baseRate + additionalRate;
        
        return amount.multiply(new BigDecimal(totalRate)).setScale(2, RoundingMode.HALF_UP);
    }

    public BigDecimal applyBulkDiscount(BigDecimal originalPrice, int quantity) {
        if (quantity >= 10) {
            BigDecimal bulkDiscountRate = new BigDecimal("0.05");
            BigDecimal discountAmount = originalPrice.multiply(bulkDiscountRate);
            return originalPrice.subtract(discountAmount);
        }
        return originalPrice;
    }

    public static class PriceItem {
        private BigDecimal unitPrice;
        private int quantity;
        private String itemCode;

        public PriceItem(BigDecimal unitPrice, int quantity, String itemCode) {
            this.unitPrice = unitPrice;
            this.quantity = quantity;
            this.itemCode = itemCode;
        }

        public BigDecimal getUnitPrice() {
            return unitPrice;
        }

        public int getQuantity() {
            return quantity;
        }

        public String getItemCode() {
            return itemCode;
        }
    }
}