package com.example.ecommerce.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import com.example.ecommerce.model.Order;
import com.example.ecommerce.model.OrderItem;
import com.example.ecommerce.model.ShippingInfo;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.ShippingRateRepository;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;

@Service
@Transactional
public class OrderShippingService {

    private static final BigDecimal FREE_SHIPPING_THRESHOLD = BigDecimal.valueOf(5000);
    private static final BigDecimal DEFAULT_SHIPPING_RATE = BigDecimal.valueOf(500);
    
    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private ShippingRateRepository shippingRateRepository;

    public BigDecimal calculateShippingCost(Order order) {
        if (order == null || order.getItems().isEmpty()) {
            return BigDecimal.ZERO;
        }

        BigDecimal orderTotal = calculateOrderTotal(order);
        BigDecimal baseShippingFee = determineBaseShippingFee(order.getShippingInfo());
        
        return applyFreeShippingPolicy(orderTotal, baseShippingFee);
    }

    private BigDecimal calculateOrderTotal(Order order) {
        return order.getItems().stream()
                .map(this::calculateItemTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal calculateItemTotal(OrderItem item) {
        return item.getUnitPrice()
                .multiply(BigDecimal.valueOf(item.getQuantity()))
                .setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal determineBaseShippingFee(ShippingInfo shippingInfo) {
        if (shippingInfo == null || shippingInfo.getRegion() == null) {
            return DEFAULT_SHIPPING_RATE;
        }

        return shippingRateRepository.findByRegion(shippingInfo.getRegion())
                .map(rate -> rate.getStandardRate())
                .orElse(DEFAULT_SHIPPING_RATE);
    }

    private BigDecimal applyFreeShippingPolicy(BigDecimal total, BigDecimal shippingFee) {
        return total.compareTo(FREE_SHIPPING_THRESHOLD) > 0 ? BigDecimal.ZERO : shippingFee;
    }

    public boolean isEligibleForFreeShipping(Order order) {
        BigDecimal orderTotal = calculateOrderTotal(order);
        return orderTotal.compareTo(FREE_SHIPPING_THRESHOLD) > 0;
    }

    @Transactional
    public Order updateOrderShipping(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));
        
        BigDecimal shippingCost = calculateShippingCost(order);
        order.setShippingCost(shippingCost);
        
        return orderRepository.save(order);
    }

    public BigDecimal calculateTotalWithShipping(Order order) {
        BigDecimal orderTotal = calculateOrderTotal(order);
        BigDecimal shippingCost = calculateShippingCost(order);
        
        return orderTotal.add(shippingCost).setScale(2, RoundingMode.HALF_UP);
    }

    private boolean hasExpressShipping(ShippingInfo shippingInfo) {
        return shippingInfo != null && 
               shippingInfo.getShippingMethod() != null && 
               shippingInfo.getShippingMethod().isExpress();
    }

    public List<Order> findOrdersEligibleForFreeShipping() {
        return orderRepository.findAll().stream()
                .filter(this::isEligibleForFreeShipping)
                .toList();
    }
}