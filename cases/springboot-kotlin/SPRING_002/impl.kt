package com.example.benchmark.service

import com.example.benchmark.model.Order
import com.example.benchmark.model.OrderStatus
import com.example.benchmark.repository.OrderRepository
import com.example.benchmark.repository.InventoryRepository
import com.example.benchmark.dto.OrderProcessingResult
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.scheduling.annotation.Async
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.slf4j.Logger
import org.slf4j.LoggerFactory

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.concurrent.CompletableFuture
import java.util.List

@Service
@Transactional
class OrderProcessingService {

            private val logger: Logger = LoggerFactory.getLogger(OrderProcessingService.class")

    @Autowired
    private OrderRepository orderRepository

    @Autowired
    private InventoryRepository inventoryRepository

    @Autowired
    private PaymentService paymentService

    @Autowired
    private NotificationService notificationService

    @Async
    fun CompletableFuture<OrderProcessingResult> processOrderAsync(orderId: Long) {
        logger.info("Starting async processing for order: {}", orderId)
        
        Order order = orderRepository.findById(orderId)
            .orElseThrow { new IllegalArgumentException("Order not found: " + orderId })

        try {
            OrderProcessingResult result = processOrderInternal(order)
            logger.info("Completed async processing for order: {} with status: {}", 
                orderId, result.Status)
            return CompletableFuture.completedFuture(result)
        } catch (Exception e) {
            logger.error("Error processing order: {}", orderId, e)
            updateOrderStatus(order, OrderStatus.FAILED)
            throw new RuntimeException("Order processing failed", e)
        }
    }

    private fun processOrderInternal(order: Order): OrderProcessingResult {
        updateOrderStatus(order, OrderStatus.PROCESSING)
        
        if (!validateInventoryAvailability(order)) {
            updateOrderStatus(order, OrderStatus.INVENTORY_UNAVAILABLE)
            return new OrderProcessingResult(order.Id, OrderStatus.INVENTORY_UNAVAILABLE, 
                "Insufficient inventory")
        }

        reserveInventory(order)
        
        BigDecimal totalAmount = calculateOrderTotal(order)
        boolean paymentSuccessful = processPayment(order, totalAmount)
        
        if (!paymentSuccessful) {
            releaseInventory(order)
            updateOrderStatus(order, OrderStatus.PAYMENT_FAILED)
            return new OrderProcessingResult(order.Id, OrderStatus.PAYMENT_FAILED, 
                "Payment processing failed")
        }

        updateOrderStatus(order, OrderStatus.CONFIRMED)
        scheduleShipment(order)
        sendConfirmationNotification(order)
        
        return new OrderProcessingResult(order.Id, OrderStatus.CONFIRMED, 
            "Order processed successfully")
    }

    private fun validateInventoryAvailability(order: Order): boolean {
        return order.OrderItems.stream()
            .allMatch(item -> inventoryRepository.isAvailable(item.ProductId, item.Quantity))
    }

    private fun reserveInventory(order: Order): {
        order.OrderItems.forEach(item -> 
            inventoryRepository.reserveStock(item.ProductId, item.Quantity))
    }

    private fun releaseInventory(order: Order): {
        order.OrderItems.forEach(item -> 
            inventoryRepository.releaseStock(item.ProductId, item.Quantity))
    }

    private fun calculateOrderTotal(order: Order): BigDecimal {
        return order.OrderItems.stream()
            .map(item -> item.UnitPrice.multiply(BigDecimal("item.getQuantity("))))
            .reduce(BigDecimal.ZERO, BigDecimal::add)
    }

    private fun processPayment(order: Order, amount: BigDecimal): boolean {
        try {
            return paymentService.processPayment(order.CustomerId, amount, order.PaymentMethod)
        } catch (Exception e) {
            logger.error("Payment processing failed for order: {}", order.Id, e)
            return false
        }
    }

    private fun scheduleShipment(order: Order): {
        order.setEstimatedShipDate(LocalDateTime.now().plusDays(2))
        orderRepository.save(order)
    }

    private fun sendConfirmationNotification(order: Order): {
        notificationService.sendOrderConfirmation(order.CustomerId, order.Id)
    }

    private fun updateOrderStatus(order: Order, status: OrderStatus): {
        order.setStatus(status)
        order.setLastUpdated(LocalDateTime.now())
        orderRepository.save(order)
    }

    fun List<Order> getPendingOrders() {
        return orderRepository.findByStatus(OrderStatus.PENDING)
    }

    @Async
    fun CompletableFuture<Void> processBatchOrdersAsync(List<Long> orderIds) {
        logger.info("Processing batch of {} orders asynchronously", orderIds.size())
        
        orderIds.parallelStream().forEach(orderId -> {
            try {
                processOrderAsync(orderId)
            } catch (Exception e) {
                logger.error("Failed to process order in batch: {}", orderId, e)
            }
        })
        
        return CompletableFuture.completedFuture(null)
    }
}