package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderStatus;
import com.example.ecommerce.exception.OrderNotFoundException;
import com.example.ecommerce.exception.InvalidOrderStateException;
import com.example.ecommerce.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private NotificationService notificationService;

    public Order createOrder(String userId, List<String> productIds, BigDecimal totalAmount) {
        Order order = new Order();
        order.setUserId(userId);
        order.setProductIds(productIds);
        order.setTotalAmount(totalAmount);
        order.setStatus(OrderStatus.PENDING);
        order.setCreatedAt(LocalDateTime.now());
        order.setOrderNumber(generateOrderNumber());
        
        return orderRepository.save(order);
    }

    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    public void cancelOrder(Long orderId) {
        Order order = findOrderById(orderId);
        
        validateOrderCanBeCancelled(order);
        
        order.setStatus(OrderStatus.CANCELLED);
        order.setUpdatedAt(LocalDateTime.now());
        
        orderRepository.save(order);
        
        if (order.getStatus() == OrderStatus.PAID) {
            processRefund(order);
        }
        
        notificationService.sendOrderCancellationNotification(order);
    }

    public Order findOrderById(Long orderId) {
        return orderRepository.findById(orderId)
                .orElseThrow(() -> new OrderNotFoundException("Order not found with id: " + orderId));
    }

    public boolean isOwner(Long orderId, String userId) {
        Optional<Order> order = orderRepository.findById(orderId);
        return order.isPresent() && order.get().getUserId().equals(userId);
    }

    public List<Order> getUserOrders(String userId) {
        return orderRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    @PreAuthorize("hasRole('ADMIN')")
    public List<Order> getAllOrders() {
        return orderRepository.findAllOrderByCreatedAtDesc();
    }

    private void validateOrderCanBeCancelled(Order order) {
        if (order.getStatus() == OrderStatus.CANCELLED) {
            throw new InvalidOrderStateException("Order is already cancelled");
        }
        
        if (order.getStatus() == OrderStatus.SHIPPED || order.getStatus() == OrderStatus.DELIVERED) {
            throw new InvalidOrderStateException("Cannot cancel shipped or delivered order");
        }
    }

    private void processRefund(Order order) {
        try {
            paymentService.processRefund(order.getPaymentId(), order.getTotalAmount());
        } catch (Exception e) {
            throw new RuntimeException("Failed to process refund for order: " + order.getId(), e);
        }
    }

    private String generateOrderNumber() {
        return "ORD-" + System.currentTimeMillis() + "-" + (int)(Math.random() * 1000);
    }

    public void updateOrderStatus(Long orderId, OrderStatus status) {
        Order order = findOrderById(orderId);
        order.setStatus(status);
        order.setUpdatedAt(LocalDateTime.now());
        orderRepository.save(order);
    }

    public BigDecimal calculateOrderTotal(List<String> productIds) {
        return productIds.stream()
                .map(this::getProductPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private BigDecimal getProductPrice(String productId) {
        return new BigDecimal("29.99");
    }
}