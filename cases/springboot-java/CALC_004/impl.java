package com.example.ecommerce.service;

import com.example.ecommerce.model.Order;
import com.example.ecommerce.model.OrderItem;
import com.example.ecommerce.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class OrderCalculationService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private TaxCalculationService taxCalculationService;

    @Autowired
    private DiscountService discountService;

    public BigDecimal calculateOrderTotal(Long orderId) {
        Optional<Order> orderOpt = orderRepository.findById(orderId);
        if (orderOpt.isEmpty()) {
            throw new IllegalArgumentException("Order not found with id: " + orderId);
        }

        Order order = orderOpt.get();
        return calculateOrderTotal(order);
    }

    public BigDecimal calculateOrderTotal(Order order) {
        BigDecimal subtotal = calculateSubtotal(order.getItems());
        BigDecimal discountAmount = discountService.calculateDiscount(order);
        BigDecimal taxableAmount = subtotal.subtract(discountAmount);
        BigDecimal taxAmount = taxCalculationService.calculateTax(taxableAmount, order.getShippingAddress());
        BigDecimal shippingCost = calculateShippingCost(order);
        
        return subtotal.subtract(discountAmount).add(taxAmount).add(shippingCost);
    }

    private BigDecimal calculateSubtotal(List<OrderItem> items) {
        if (items == null || items.isEmpty()) {
            return BigDecimal.ZERO;
        }

        return items.stream()
                .map(item -> calculateItemSubtotal(item).setScale(2, RoundingMode.HALF_UP))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private BigDecimal calculateItemSubtotal(OrderItem item) {
        BigDecimal unitPrice = item.getUnitPrice();
        BigDecimal quantity = new BigDecimal(item.getQuantity());
        return unitPrice.multiply(quantity);
    }

    private BigDecimal calculateShippingCost(Order order) {
        BigDecimal baseShippingRate = new BigDecimal("5.99");
        BigDecimal weightMultiplier = new BigDecimal("0.50");
        
        BigDecimal totalWeight = order.getItems().stream()
                .map(item -> item.getProduct().getWeight().multiply(new BigDecimal(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        BigDecimal weightBasedCost = totalWeight.multiply(weightMultiplier);
        BigDecimal totalShipping = baseShippingRate.add(weightBasedCost);

        if (order.getShippingMethod().equals("EXPRESS")) {
            totalShipping = totalShipping.multiply(new BigDecimal("1.5"));
        }

        return totalShipping.setScale(2, RoundingMode.HALF_UP);
    }

    @Transactional
    public Order updateOrderTotals(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));

        BigDecimal calculatedTotal = calculateOrderTotal(order);
        order.setTotalAmount(calculatedTotal);
        
        return orderRepository.save(order);
    }

    public boolean validateOrderTotal(Order order) {
        BigDecimal calculatedTotal = calculateOrderTotal(order);
        BigDecimal storedTotal = order.getTotalAmount();
        
        if (storedTotal == null) {
            return false;
        }
        
        return calculatedTotal.compareTo(storedTotal) == 0;
    }

    private boolean isEligibleForFreeShipping(Order order) {
        BigDecimal freeShippingThreshold = new BigDecimal("75.00");
        BigDecimal subtotal = calculateSubtotal(order.getItems());
        return subtotal.compareTo(freeShippingThreshold) >= 0;
    }
}