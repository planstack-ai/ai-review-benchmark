package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.Payment;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.PaymentRepository;
import com.example.ecommerce.exception.PaymentProcessingException;
import com.example.ecommerce.exception.InsufficientInventoryException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.annotation.Propagation;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class OrderProcessingService {

    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private PaymentRepository paymentRepository;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Autowired
    private PaymentGatewayService paymentGatewayService;
    
    @Autowired
    private NotificationService notificationService;

    @Transactional
    public Order processOrder(String customerId, String productId, Integer quantity, BigDecimal unitPrice) {
        validateOrderRequest(customerId, productId, quantity, unitPrice);
        
        BigDecimal totalAmount = calculateTotalAmount(quantity, unitPrice);
        
        Order order = createOrder(customerId, productId, quantity, totalAmount);
        order = orderRepository.save(order);
        
        try {
            reserveInventory(productId, quantity);
            Payment payment = processPayment(order.getId(), customerId, totalAmount);
            
            order.setPaymentId(payment.getId());
            order.setStatus("COMPLETED");
            order.setCompletedAt(LocalDateTime.now());
            
            orderRepository.save(order);
            
            sendOrderConfirmation(customerId, order);
            
            return order;
            
        } catch (Exception e) {
            order.setStatus("FAILED");
            order.setFailureReason(e.getMessage());
            orderRepository.save(order);
            throw e;
        }
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public Payment processPayment(String orderId, String customerId, BigDecimal amount) {
        Payment payment = new Payment();
        payment.setId(UUID.randomUUID().toString());
        payment.setOrderId(orderId);
        payment.setCustomerId(customerId);
        payment.setAmount(amount);
        payment.setStatus("PENDING");
        payment.setCreatedAt(LocalDateTime.now());
        
        payment = paymentRepository.save(payment);
        
        boolean paymentSuccessful = paymentGatewayService.chargeCustomer(customerId, amount);
        
        if (paymentSuccessful) {
            payment.setStatus("COMPLETED");
            payment.setProcessedAt(LocalDateTime.now());
        } else {
            payment.setStatus("FAILED");
            payment.setFailureReason("Payment gateway declined transaction");
            throw new PaymentProcessingException("Payment failed for order: " + orderId);
        }
        
        return paymentRepository.save(payment);
    }

    private void validateOrderRequest(String customerId, String productId, Integer quantity, BigDecimal unitPrice) {
        if (customerId == null || customerId.trim().isEmpty()) {
            throw new IllegalArgumentException("Customer ID cannot be null or empty");
        }
        if (productId == null || productId.trim().isEmpty()) {
            throw new IllegalArgumentException("Product ID cannot be null or empty");
        }
        if (quantity == null || quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be greater than zero");
        }
        if (unitPrice == null || unitPrice.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Unit price must be greater than zero");
        }
    }

    private BigDecimal calculateTotalAmount(Integer quantity, BigDecimal unitPrice) {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }

    private Order createOrder(String customerId, String productId, Integer quantity, BigDecimal totalAmount) {
        Order order = new Order();
        order.setId(UUID.randomUUID().toString());
        order.setCustomerId(customerId);
        order.setProductId(productId);
        order.setQuantity(quantity);
        order.setTotalAmount(totalAmount);
        order.setStatus("PROCESSING");
        order.setCreatedAt(LocalDateTime.now());
        return order;
    }

    private void reserveInventory(String productId, Integer quantity) {
        if (!inventoryService.reserveStock(productId, quantity)) {
            throw new InsufficientInventoryException("Insufficient inventory for product: " + productId);
        }
    }

    private void sendOrderConfirmation(String customerId, Order order) {
        notificationService.sendOrderConfirmation(customerId, order.getId());
    }
}