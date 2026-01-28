package com.example.benchmark.service;

import com.example.benchmark.model.Order;
import com.example.benchmark.model.OrderStatus;
import com.example.benchmark.repository.OrderRepository;
import com.example.benchmark.repository.InventoryRepository;
import com.example.benchmark.dto.OrderProcessingResult;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;
import java.util.List;

@Service
@Transactional
public class OrderProcessingService {

    private static final Logger logger = LoggerFactory.getLogger(OrderProcessingService.class);

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private InventoryRepository inventoryRepository;

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private NotificationService notificationService;

    @Async
    public CompletableFuture<OrderProcessingResult> processOrderAsync(Long orderId) {
        logger.info("Starting async processing for order: {}", orderId);
        
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        try {
            OrderProcessingResult result = processOrderInternal(order);
            logger.info("Completed async processing for order: {} with status: {}", 
                orderId, result.getStatus());
            return CompletableFuture.completedFuture(result);
        } catch (Exception e) {
            logger.error("Error processing order: {}", orderId, e);
            updateOrderStatus(order, OrderStatus.FAILED);
            throw new RuntimeException("Order processing failed", e);
        }
    }

    private OrderProcessingResult processOrderInternal(Order order) {
        updateOrderStatus(order, OrderStatus.PROCESSING);
        
        if (!validateInventoryAvailability(order)) {
            updateOrderStatus(order, OrderStatus.INVENTORY_UNAVAILABLE);
            return new OrderProcessingResult(order.getId(), OrderStatus.INVENTORY_UNAVAILABLE, 
                "Insufficient inventory");
        }

        reserveInventory(order);
        
        BigDecimal totalAmount = calculateOrderTotal(order);
        boolean paymentSuccessful = processPayment(order, totalAmount);
        
        if (!paymentSuccessful) {
            releaseInventory(order);
            updateOrderStatus(order, OrderStatus.PAYMENT_FAILED);
            return new OrderProcessingResult(order.getId(), OrderStatus.PAYMENT_FAILED, 
                "Payment processing failed");
        }

        updateOrderStatus(order, OrderStatus.CONFIRMED);
        scheduleShipment(order);
        sendConfirmationNotification(order);
        
        return new OrderProcessingResult(order.getId(), OrderStatus.CONFIRMED, 
            "Order processed successfully");
    }

    private boolean validateInventoryAvailability(Order order) {
        return order.getOrderItems().stream()
            .allMatch(item -> inventoryRepository.isAvailable(item.getProductId(), item.getQuantity()));
    }

    private void reserveInventory(Order order) {
        order.getOrderItems().forEach(item -> 
            inventoryRepository.reserveStock(item.getProductId(), item.getQuantity()));
    }

    private void releaseInventory(Order order) {
        order.getOrderItems().forEach(item -> 
            inventoryRepository.releaseStock(item.getProductId(), item.getQuantity()));
    }

    private BigDecimal calculateOrderTotal(Order order) {
        return order.getOrderItems().stream()
            .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private boolean processPayment(Order order, BigDecimal amount) {
        try {
            return paymentService.processPayment(order.getCustomerId(), amount, order.getPaymentMethod());
        } catch (Exception e) {
            logger.error("Payment processing failed for order: {}", order.getId(), e);
            return false;
        }
    }

    private void scheduleShipment(Order order) {
        order.setEstimatedShipDate(LocalDateTime.now().plusDays(2));
        orderRepository.save(order);
    }

    private void sendConfirmationNotification(Order order) {
        notificationService.sendOrderConfirmation(order.getCustomerId(), order.getId());
    }

    private void updateOrderStatus(Order order, OrderStatus status) {
        order.setStatus(status);
        order.setLastUpdated(LocalDateTime.now());
        orderRepository.save(order);
    }

    public List<Order> getPendingOrders() {
        return orderRepository.findByStatus(OrderStatus.PENDING);
    }

    @Async
    public CompletableFuture<Void> processBatchOrdersAsync(List<Long> orderIds) {
        logger.info("Processing batch of {} orders asynchronously", orderIds.size());
        
        orderIds.parallelStream().forEach(orderId -> {
            try {
                processOrderAsync(orderId);
            } catch (Exception e) {
                logger.error("Failed to process order in batch: {}", orderId, e);
            }
        });
        
        return CompletableFuture.completedFuture(null);
    }
}