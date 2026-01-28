package com.example.service;

import com.example.model.Order;
import com.example.model.OrderStatus;
import com.example.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@Transactional
public class OrderProcessingService {

    private final OrderRepository orderRepository;
    private final Set<OrderStatus> completedStatuses;

    @Autowired
    public OrderProcessingService(OrderRepository orderRepository) {
        this.orderRepository = orderRepository;
        this.completedStatuses = Set.of(
            OrderStatus.DELIVERED,
            OrderStatus.COMPLETED,
            OrderStatus.FULFILLED
        );
    }

    public boolean processOrderCompletion(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        if (isOrderCompleted(order)) {
            updateCompletionMetrics(order);
            return true;
        }

        return false;
    }

    public List<Order> getCompletedOrdersForCustomer(Long customerId) {
        List<Order> customerOrders = orderRepository.findByCustomerId(customerId);
        return customerOrders.stream()
            .filter(this::isOrderCompleted)
            .collect(Collectors.toList());
    }

    public BigDecimal calculateCompletedOrdersRevenue(List<Order> orders) {
        return orders.stream()
            .filter(this::isOrderCompleted)
            .map(Order::getTotalAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public void markOrderAsCompleted(Long orderId, OrderStatus completionStatus) {
        if (!isValidCompletionStatus(completionStatus)) {
            throw new IllegalArgumentException("Invalid completion status: " + completionStatus);
        }

        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        order.setStatus(completionStatus);
        order.setCompletedAt(LocalDateTime.now());
        orderRepository.save(order);
    }

    private boolean isOrderCompleted(Order order) {
        if (order == null || order.getStatus() == null) {
            return false;
        }
        return completedStatuses.stream()
            .anyMatch(s -> s.name().equals(order.getStatus().name()));
    }

    private boolean isValidCompletionStatus(OrderStatus status) {
        return completedStatuses.stream()
            .anyMatch(s -> s == status);
    }

    private void updateCompletionMetrics(Order order) {
        order.setProcessedAt(LocalDateTime.now());
        BigDecimal processingFee = calculateProcessingFee(order.getTotalAmount());
        order.setProcessingFee(processingFee);
        orderRepository.save(order);
    }

    private BigDecimal calculateProcessingFee(BigDecimal orderAmount) {
        BigDecimal feeRate = new BigDecimal("0.025");
        return orderAmount.multiply(feeRate);
    }

    public int getCompletedOrderCount(List<Order> orders) {
        return (int) orders.stream()
            .filter(this::isOrderCompleted)
            .count();
    }
}