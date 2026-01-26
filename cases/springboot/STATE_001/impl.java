package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderStatus;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.exception.OrderNotFoundException;
import com.example.ecommerce.exception.InvalidOrderOperationException;
import org.springframework.beans.factory.annotation.Autowired;
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
    private InventoryService inventoryService;

    @Autowired
    private NotificationService notificationService;

    public Order createOrder(Long customerId, List<Long> productIds, BigDecimal totalAmount) {
        validateOrderCreation(customerId, productIds, totalAmount);
        
        Order order = new Order();
        order.setCustomerId(customerId);
        order.setProductIds(productIds);
        order.setTotalAmount(totalAmount);
        order.setStatus(OrderStatus.PENDING);
        order.setCreatedAt(LocalDateTime.now());
        
        Order savedOrder = orderRepository.save(order);
        notificationService.sendOrderCreatedNotification(savedOrder);
        
        return savedOrder;
    }

    public Order confirmOrder(Long orderId) {
        Order order = findOrderById(orderId);
        
        if (order.getStatus() != OrderStatus.PENDING) {
            throw new InvalidOrderOperationException("Order can only be confirmed from PENDING state");
        }
        
        if (!inventoryService.reserveItems(order.getProductIds())) {
            throw new InvalidOrderOperationException("Insufficient inventory for order confirmation");
        }
        
        order.setStatus(OrderStatus.CONFIRMED);
        order.setConfirmedAt(LocalDateTime.now());
        
        Order confirmedOrder = orderRepository.save(order);
        notificationService.sendOrderConfirmedNotification(confirmedOrder);
        
        return confirmedOrder;
    }

    public Order cancelOrder(Long orderId) {
        Order order = findOrderById(orderId);
        
        validateOrderCancellation(order);
        
        if (order.getStatus() == OrderStatus.CONFIRMED) {
            inventoryService.releaseReservedItems(order.getProductIds());
        }
        
        order.cancel();
        order.setCancelledAt(LocalDateTime.now());
        
        Order cancelledOrder = orderRepository.save(order);
        notificationService.sendOrderCancelledNotification(cancelledOrder);
        
        return cancelledOrder;
    }

    public Order shipOrder(Long orderId) {
        Order order = findOrderById(orderId);
        
        if (order.getStatus() != OrderStatus.CONFIRMED) {
            throw new InvalidOrderOperationException("Order can only be shipped from CONFIRMED state");
        }
        
        if (!paymentService.processPayment(order.getTotalAmount(), order.getCustomerId())) {
            throw new InvalidOrderOperationException("Payment processing failed for order shipment");
        }
        
        order.setStatus(OrderStatus.SHIPPED);
        order.setShippedAt(LocalDateTime.now());
        
        Order shippedOrder = orderRepository.save(order);
        notificationService.sendOrderShippedNotification(shippedOrder);
        
        return shippedOrder;
    }

    private Order findOrderById(Long orderId) {
        Optional<Order> orderOptional = orderRepository.findById(orderId);
        if (!orderOptional.isPresent()) {
            throw new OrderNotFoundException("Order not found with ID: " + orderId);
        }
        return orderOptional.get();
    }

    private void validateOrderCreation(Long customerId, List<Long> productIds, BigDecimal totalAmount) {
        if (customerId == null || productIds == null || productIds.isEmpty()) {
            throw new InvalidOrderOperationException("Invalid order parameters");
        }
        
        if (totalAmount == null || totalAmount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidOrderOperationException("Order total must be greater than zero");
        }
    }

    private void validateOrderCancellation(Order order) {
        if (order.getCancelledAt() != null) {
            throw new InvalidOrderOperationException("Order is already cancelled");
        }
    }

    public List<Order> getOrdersByCustomer(Long customerId) {
        return orderRepository.findByCustomerIdOrderByCreatedAtDesc(customerId);
    }

    public Order getOrderById(Long orderId) {
        return findOrderById(orderId);
    }
}