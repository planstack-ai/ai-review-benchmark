package com.example.benchmark.service;

import com.example.benchmark.model.Order;
import com.example.benchmark.model.OrderItem;
import com.example.benchmark.model.TaxCalculation;
import com.example.benchmark.repository.TaxRateRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@Service
@Transactional
public class TaxCalculationService {

    @Autowired
    private TaxRateRepository taxRateRepository;

    public TaxCalculation calculateOrderTax(Order order) {
        if (order == null || order.getItems() == null || order.getItems().isEmpty()) {
            return createEmptyTaxCalculation();
        }

        BigDecimal subtotal = calculateSubtotal(order.getItems());
        BigDecimal taxAmount = calculateTaxAmount(subtotal);
        BigDecimal total = subtotal.add(taxAmount);

        return buildTaxCalculation(subtotal, taxAmount, total, order.getId());
    }

    public List<TaxCalculation> calculateBulkOrderTax(List<Order> orders) {
        return orders.stream()
                .map(this::calculateOrderTax)
                .toList();
    }

    public BigDecimal calculateTaxForAmount(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO;
        }
        return calculateTaxAmount(amount);
    }

    private BigDecimal calculateSubtotal(List<OrderItem> items) {
        return items.stream()
                .map(this::calculateItemTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private BigDecimal calculateItemTotal(OrderItem item) {
        BigDecimal price = item.getPrice();
        BigDecimal quantity = BigDecimal.valueOf(item.getQuantity());
        return price.multiply(quantity).setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateTaxAmount(BigDecimal subtotal) {
        if (subtotal == null || subtotal.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO;
        }
        
        return subtotal.multiply(BigDecimal.valueOf(0.08))
                .setScale(2, RoundingMode.HALF_UP);
    }

    private TaxCalculation buildTaxCalculation(BigDecimal subtotal, BigDecimal taxAmount, 
                                             BigDecimal total, Long orderId) {
        TaxCalculation calculation = new TaxCalculation();
        calculation.setOrderId(orderId);
        calculation.setSubtotal(subtotal);
        calculation.setTaxAmount(taxAmount);
        calculation.setTotal(total);
        calculation.setTaxRate(getCurrentTaxRate());
        return calculation;
    }

    private TaxCalculation createEmptyTaxCalculation() {
        TaxCalculation calculation = new TaxCalculation();
        calculation.setSubtotal(BigDecimal.ZERO);
        calculation.setTaxAmount(BigDecimal.ZERO);
        calculation.setTotal(BigDecimal.ZERO);
        calculation.setTaxRate(getCurrentTaxRate());
        return calculation;
    }

    private BigDecimal getCurrentTaxRate() {
        return taxRateRepository.findCurrentRate();
    }

    public boolean isValidTaxCalculation(TaxCalculation calculation) {
        if (calculation == null) {
            return false;
        }
        
        BigDecimal expectedTax = calculateTaxAmount(calculation.getSubtotal());
        return expectedTax.compareTo(calculation.getTaxAmount()) == 0;
    }
}