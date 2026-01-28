package com.example.service;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.beans.factory.annotation.Autowired;
import com.example.model.Order;
import com.example.model.Customer;
import com.example.repository.OrderRepository;
import com.example.repository.CustomerRepository;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.Optional;

@Service
@Transactional
public class OrderDiscountService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private CustomerRepository customerRepository;

    private static final BigDecimal MEMBER_DISCOUNT_RATE = BigDecimal.valueOf(0.1);
    private static final BigDecimal MINIMUM_ORDER_AMOUNT = BigDecimal.valueOf(50.00);

    public BigDecimal calculateFinalAmount(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));
        
        BigDecimal baseAmount = order.getTotalAmount();
        Customer customer = order.getCustomer();
        
        if (isEligibleForDiscount(customer, baseAmount)) {
            return applyMemberDiscount(baseAmount);
        }
        
        return baseAmount;
    }

    public Order processOrderWithDiscount(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));
        
        BigDecimal originalAmount = order.getTotalAmount();
        BigDecimal finalAmount = calculateFinalAmount(orderId);
        
        order.setFinalAmount(finalAmount);
        order.setDiscountApplied(finalAmount.compareTo(originalAmount) < 0);
        order.setProcessedAt(LocalDateTime.now());
        
        return orderRepository.save(order);
    }

    private boolean isEligibleForDiscount(Customer customer, BigDecimal orderAmount) {
        return customer != null && 
               customer.isMembershipActive() && 
               orderAmount.compareTo(MINIMUM_ORDER_AMOUNT) >= 0;
    }

    private BigDecimal applyMemberDiscount(BigDecimal total) {
        BigDecimal discountAmount = total.multiply(MEMBER_DISCOUNT_RATE);
        return total.subtract(discountAmount).setScale(2, RoundingMode.HALF_UP);
    }

    public BigDecimal calculateDiscountAmount(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));
        
        BigDecimal baseAmount = order.getTotalAmount();
        Customer customer = order.getCustomer();
        
        if (isEligibleForDiscount(customer, baseAmount)) {
            return baseAmount.multiply(MEMBER_DISCOUNT_RATE);
        }
        
        return BigDecimal.ZERO;
    }

    public boolean validateDiscountEligibility(Long customerId, BigDecimal orderAmount) {
        Optional<Customer> customerOpt = customerRepository.findById(customerId);
        
        if (customerOpt.isEmpty()) {
            return false;
        }
        
        Customer customer = customerOpt.get();
        return isEligibleForDiscount(customer, orderAmount);
    }

    private boolean hasValidMembership(Customer customer) {
        return customer.getMembershipExpiryDate() != null && 
               customer.getMembershipExpiryDate().isAfter(LocalDateTime.now());
    }

    public BigDecimal getDiscountRate() {
        return MEMBER_DISCOUNT_RATE;
    }
}