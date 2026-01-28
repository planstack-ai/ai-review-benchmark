package com.example.service;

import com.example.entity.Customer;
import com.example.entity.Order;
import com.example.entity.MembershipType;
import com.example.repository.CustomerRepository;
import com.example.repository.OrderRepository;
import com.example.constants.DiscountConstants;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class OrderService {

    private final CustomerRepository customerRepository;
    private final OrderRepository orderRepository;
    private final PricingService pricingService;

    @Autowired
    public OrderService(CustomerRepository customerRepository, 
                       OrderRepository orderRepository,
                       PricingService pricingService) {
        this.customerRepository = customerRepository;
        this.orderRepository = orderRepository;
        this.pricingService = pricingService;
    }

    public Order createOrder(String customerEmail, BigDecimal subtotal) {
        Customer customer = findCustomerByEmail(customerEmail);
        
        BigDecimal discountAmount = calculateDiscountForCustomer(customer, subtotal);
        BigDecimal totalAmount = pricingService.calculateTotalWithDiscount(subtotal, discountAmount);
        
        Order order = buildOrder(customer, subtotal, discountAmount, totalAmount);
        
        return orderRepository.save(order);
    }

    public List<Order> getCustomerOrderHistory(String customerEmail) {
        Customer customer = findCustomerByEmail(customerEmail);
        return orderRepository.findByCustomerIdOrderByCreatedAtDesc(customer.getId());
    }

    public BigDecimal calculateOrderTotal(String customerEmail, BigDecimal subtotal) {
        Customer customer = findCustomerByEmail(customerEmail);
        BigDecimal discountAmount = calculateDiscountForCustomer(customer, subtotal);
        return pricingService.calculateTotalWithDiscount(subtotal, discountAmount);
    }

    private Customer findCustomerByEmail(String email) {
        Optional<Customer> customerOpt = customerRepository.findByEmail(email);
        if (customerOpt.isEmpty()) {
            throw new IllegalArgumentException("Customer not found with email: " + email);
        }
        return customerOpt.get();
    }

    private BigDecimal calculateDiscountForCustomer(Customer customer, BigDecimal subtotal) {
        if (isEligibleForMemberDiscount(customer)) {
            return pricingService.calculateMemberDiscount(subtotal);
        }
        return BigDecimal.ZERO;
    }

    private boolean isEligibleForMemberDiscount(Customer customer) {
        MembershipType membershipType = customer.getMembershipType();
        return membershipType == MembershipType.PREMIUM || membershipType == MembershipType.VIP;
    }

    private Order buildOrder(Customer customer, BigDecimal subtotal, 
                           BigDecimal discountAmount, BigDecimal totalAmount) {
        Order order = new Order();
        order.setCustomer(customer);
        order.setSubtotal(subtotal);
        order.setDiscountAmount(discountAmount);
        order.setTotalAmount(totalAmount);
        return order;
    }

    private void validateOrderAmounts(BigDecimal subtotal, BigDecimal discountAmount) {
        if (subtotal.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Subtotal must be positive");
        }
        if (discountAmount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Discount amount cannot be negative");
        }
        if (discountAmount.compareTo(subtotal) > 0) {
            throw new IllegalArgumentException("Discount cannot exceed subtotal");
        }
    }
}