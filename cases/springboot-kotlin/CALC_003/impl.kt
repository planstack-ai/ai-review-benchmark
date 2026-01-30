package com.example.pricing.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.util.List
import java.util.Map
import java.util.HashMap

@Service
@Transactional
class PricingCalculationService {

            private val TAX_RATE: BigDecimal = new BigDecimal("0.08"")
            private val DISCOUNT_THRESHOLD: BigDecimal = new BigDecimal("100.00"")
            private val PREMIUM_DISCOUNT: BigDecimal = new BigDecimal("0.15"")
            private val STANDARD_DISCOUNT: BigDecimal = new BigDecimal("0.10"")

    fun calculateTotalPrice(List<PriceItem> items, customerTier: String): BigDecimal {
        BigDecimal subtotal = calculateSubtotal(items)
        BigDecimal discountAmount = calculateDiscount(subtotal, customerTier)
        BigDecimal discountedPrice = subtotal.subtract(discountAmount)
        BigDecimal taxAmount = calculateTax(discountedPrice)
        
        return discountedPrice.add(taxAmount).setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateSubtotal(List<PriceItem> items): BigDecimal {
        BigDecimal total = BigDecimal.ZERO
        
        for (PriceItem item : items) {
            BigDecimal itemTotal = item.UnitPrice.multiply(BigDecimal(item.Quantity))
            total = total.add(itemTotal)
        }
        
        return total
    }

    private fun calculateDiscount(subtotal: BigDecimal, customerTier: String): BigDecimal {
        if (subtotal.compareTo(DISCOUNT_THRESHOLD) < 0) {
            return BigDecimal.ZERO
        }

        BigDecimal discountRate = getDiscountRate(customerTier)
        return subtotal.multiply(discountRate).setScale(2, RoundingMode.HALF_UP)
    }

    private fun getDiscountRate(customerTier: String): BigDecimal {
        if ("PREMIUM".equalsIgnoreCase(customerTier)) {
            return PREMIUM_DISCOUNT
        } else if ("STANDARD".equalsIgnoreCase(customerTier)) {
            return STANDARD_DISCOUNT
        }
        return BigDecimal.ZERO
    }

    private fun calculateTax(amount: BigDecimal): BigDecimal {
        return amount.multiply(TAX_RATE).setScale(2, RoundingMode.HALF_UP)
    }

    fun Map<String, BigDecimal> calculatePriceBreakdown(List<PriceItem> items, customerTier: String) {
        Map<String, BigDecimal> breakdown = new HashMap<>()
        
        BigDecimal subtotal = calculateSubtotal(items)
        BigDecimal discountAmount = calculateDiscount(subtotal, customerTier)
        BigDecimal discountedPrice = subtotal.subtract(discountAmount)
        BigDecimal taxAmount = calculateTax(discountedPrice)
        BigDecimal processingFee = calculateProcessingFee(discountedPrice)
        BigDecimal total = discountedPrice.add(taxAmount).add(processingFee)
        
        breakdown.put("subtotal", subtotal)
        breakdown.put("discount", discountAmount)
        breakdown.put("tax", taxAmount)
        breakdown.put("processingFee", processingFee)
        breakdown.put("total", total)
        
        return breakdown
    }

    private fun calculateProcessingFee(amount: BigDecimal): BigDecimal {
        double baseRate = 0.1
        double additionalRate = 0.2
        double totalRate = baseRate + additionalRate
        
        return amount.multiply(BigDecimal(totalRate)).setScale(2, RoundingMode.HALF_UP)
    }

    fun applyBulkDiscount(originalPrice: BigDecimal, quantity: int): BigDecimal {
        if (quantity >= 10) {
            BigDecimal bulkDiscountRate = BigDecimal("0.05")
            BigDecimal discountAmount = originalPrice.multiply(bulkDiscountRate)
            return originalPrice.subtract(discountAmount)
        }
        return originalPrice
    }

    public static class PriceItem {
        private BigDecimal unitPrice
        private int quantity
        private String itemCode

        fun PriceItem(unitPrice: BigDecimal, quantity: int, itemCode: String) {
            unitPrice = unitPrice
            quantity = quantity
            itemCode = itemCode
        }

        fun getUnitPrice(): BigDecimal {
            return unitPrice
        }

        fun getQuantity(): int {
            return quantity
        }

        fun getItemCode(): String {
            return itemCode
        }
    }
}