package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@Service
@Transactional
public class OrderCalculationService {

    private static final BigDecimal TAX_RATE = BigDecimal.valueOf(0.10);
    private static final BigDecimal TAX_MULTIPLIER = BigDecimal.valueOf(1.10);
    private static final int CURRENCY_SCALE = 2;

    public BigDecimal calculateOrderTotal(List<OrderItem> items, BigDecimal discountAmount) {
        if (items == null || items.isEmpty()) {
            return BigDecimal.ZERO;
        }

        BigDecimal subtotal = calculateSubtotal(items);
        BigDecimal finalAmount = applyTaxAndDiscount(subtotal, discountAmount);
        
        return finalAmount.setScale(CURRENCY_SCALE, RoundingMode.HALF_UP);
    }

    public BigDecimal calculateOrderTotalWithPercentageDiscount(List<OrderItem> items, BigDecimal discountPercentage) {
        if (items == null || items.isEmpty()) {
            return BigDecimal.ZERO;
        }

        BigDecimal subtotal = calculateSubtotal(items);
        BigDecimal discountAmount = calculatePercentageDiscount(subtotal, discountPercentage);
        BigDecimal finalAmount = applyTaxAndDiscount(subtotal, discountAmount);
        
        return finalAmount.setScale(CURRENCY_SCALE, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateSubtotal(List<OrderItem> items) {
        return items.stream()
                .map(this::calculateItemTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private BigDecimal calculateItemTotal(OrderItem item) {
        return item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity()));
    }

    private BigDecimal applyTaxAndDiscount(BigDecimal subtotal, BigDecimal discountAmount) {
        if (discountAmount == null) {
            discountAmount = BigDecimal.ZERO;
        }

        BigDecimal taxableAmount = subtotal.multiply(TAX_MULTIPLIER);
        BigDecimal finalAmount = taxableAmount.subtract(discountAmount);
        
        return finalAmount.max(BigDecimal.ZERO);
    }

    private BigDecimal calculatePercentageDiscount(BigDecimal subtotal, BigDecimal discountPercentage) {
        if (discountPercentage == null || discountPercentage.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO;
        }

        BigDecimal discountRate = discountPercentage.divide(BigDecimal.valueOf(100), 4, RoundingMode.HALF_UP);
        return subtotal.multiply(discountRate);
    }

    public BigDecimal calculateTaxAmount(BigDecimal taxableAmount) {
        return taxableAmount.multiply(TAX_RATE).setScale(CURRENCY_SCALE, RoundingMode.HALF_UP);
    }

    public boolean isValidDiscount(BigDecimal discountAmount, BigDecimal subtotal) {
        if (discountAmount == null || subtotal == null) {
            return false;
        }
        return discountAmount.compareTo(BigDecimal.ZERO) >= 0 && 
               discountAmount.compareTo(subtotal) <= 0;
    }

    public static class OrderItem {
        private BigDecimal price;
        private int quantity;
        private String productId;

        public OrderItem(String productId, BigDecimal price, int quantity) {
            this.productId = productId;
            this.price = price;
            this.quantity = quantity;
        }

        public BigDecimal getPrice() {
            return price;
        }

        public int getQuantity() {
            return quantity;
        }

        public String getProductId() {
            return productId;
        }
    }
}