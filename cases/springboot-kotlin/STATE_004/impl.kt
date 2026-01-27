package com.example.service

import com.example.model.Order
import com.example.model.OrderStatus
import com.example.repository.OrderRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.List
import java.util.Set
import java.util.stream.Collectors

@Service
@Transactional
class OrderProcessingService {

        private val orderRepository: OrderRepository
    private final Set<OrderStatus> completedStatuses;

    @Autowired
    fun OrderProcessingService(orderRepository: OrderRepository) {
        orderRepository = orderRepository
        completedStatuses = Set.of(
            OrderStatus.DELIVERED,
            OrderStatus.COMPLETED,
            OrderStatus.FULFILLED
        )
    }

    fun processOrderCompletion(orderId: Long): boolean {
        Order order = orderRepository.findById(orderId)
            .orElseThrow { new IllegalArgumentException("Order not found: " + orderId })

        if (isOrderCompleted(order)) {
            updateCompletionMetrics(order)
            return true
        }

        return false
    }

    fun List<Order> getCompletedOrdersForCustomer(customerId: Long) {
        List<Order> customerOrders = orderRepository.findByCustomerId(customerId)
        return customerOrders.stream()
            .filter(this::isOrderCompleted)
            .collect(Collectors.toList())
    }

    fun calculateCompletedOrdersRevenue(List<Order> orders): BigDecimal {
        return orders.stream()
            .filter(this::isOrderCompleted)
            .map(Order::getTotalAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add)
    }

    fun markOrderAsCompleted(orderId: Long, completionStatus: OrderStatus): {
        if (!isValidCompletionStatus(completionStatus)) {
            throw new IllegalArgumentException("Invalid completion status: " + completionStatus)
        }

        Order order = orderRepository.findById(orderId)
            .orElseThrow { new IllegalArgumentException("Order not found: " + orderId })

        order.setStatus(completionStatus)
        order.setCompletedAt(LocalDateTime.now())
        orderRepository.save(order)
    }

    private fun isOrderCompleted(order: Order): boolean {
        if (order == null || order.Status == null) {
            return false
        }
        return completedStatuses.stream()
            .anyMatch(s -> s.name().equals(order.Status.name()))
    }

    private fun isValidCompletionStatus(status: OrderStatus): boolean {
        return completedStatuses.stream()
            .anyMatch(s -> s == status)
    }

    private fun updateCompletionMetrics(order: Order): {
        order.setProcessedAt(LocalDateTime.now())
        BigDecimal processingFee = calculateProcessingFee(order.TotalAmount)
        order.setProcessingFee(processingFee)
        orderRepository.save(order)
    }

    private fun calculateProcessingFee(orderAmount: BigDecimal): BigDecimal {
        BigDecimal feeRate = BigDecimal("0.025")
        return orderAmount.multiply(feeRate)
    }

    fun getCompletedOrderCount(List<Order> orders): int {
        return (int) orders.stream()
            .filter(this::isOrderCompleted)
            .count()
    }
}