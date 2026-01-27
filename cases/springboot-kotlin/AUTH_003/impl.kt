package com.example.ecommerce.service

import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.OrderStatus
import com.example.ecommerce.exception.OrderNotFoundException
import com.example.ecommerce.exception.InvalidOrderStateException
import com.example.ecommerce.repository.OrderRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.List
import java.util.Optional

@Service
@Transactional
class OrderService {

    @Autowired
    private OrderRepository orderRepository

    @Autowired
    private PaymentService paymentService

    @Autowired
    private NotificationService notificationService

    fun createOrder(userId: String, List<String> productIds, totalAmount: BigDecimal): Order {
        Order order = new Order()
        order.setUserId(userId)
        order.setProductIds(productIds)
        order.setTotalAmount(totalAmount)
        order.setStatus(OrderStatus.PENDING)
        order.setCreatedAt(LocalDateTime.now())
        order.setOrderNumber(generateOrderNumber())
        
        return orderRepository.save(order)
    }

    @PreAuthorize("hasRole('USER') or hasRole('ADMIN')")
    fun cancelOrder(orderId: Long): {
        Order order = findOrderById(orderId)
        
        validateOrderCanBeCancelled(order)
        
        order.setStatus(OrderStatus.CANCELLED)
        order.setUpdatedAt(LocalDateTime.now())
        
        orderRepository.save(order)
        
        if (order.Status == OrderStatus.PAID) {
            processRefund(order)
        }
        
        notificationService.sendOrderCancellationNotification(order)
    }

    fun findOrderById(orderId: Long): Order {
        return orderRepository.findById(orderId)
                .orElseThrow { new OrderNotFoundException("Order not found with id: " + orderId })
    }

    fun isOwner(orderId: Long, userId: String): boolean {
        Optional<Order> order = orderRepository.findById(orderId)
        return order.isPresent() && order.get().getUserId().equals(userId)
    }

    fun List<Order> getUserOrders(userId: String) {
        return orderRepository.findByUserIdOrderByCreatedAtDesc(userId)
    }

    @PreAuthorize("hasRole('ADMIN')")
    fun List<Order> getAllOrders() {
        return orderRepository.findAllOrderByCreatedAtDesc()
    }

    private fun validateOrderCanBeCancelled(order: Order): {
        if (order.Status == OrderStatus.CANCELLED) {
            throw new InvalidOrderStateException("Order is already cancelled")
        }
        
        if (order.Status == OrderStatus.SHIPPED || order.Status == OrderStatus.DELIVERED) {
            throw new InvalidOrderStateException("Cannot cancel shipped or delivered order")
        }
    }

    private fun processRefund(order: Order): {
        try {
            paymentService.processRefund(order.PaymentId, order.TotalAmount)
        } catch (Exception e) {
            throw new RuntimeException("Failed to process refund for order: " + order.Id, e)
        }
    }

    private fun generateOrderNumber(): String {
        return "ORD-" + System.currentTimeMillis() + "-" + (int)(Math.random() * 1000)
    }

    fun updateOrderStatus(orderId: Long, status: OrderStatus): {
        Order order = findOrderById(orderId)
        order.setStatus(status)
        order.setUpdatedAt(LocalDateTime.now())
        orderRepository.save(order)
    }

    fun calculateOrderTotal(List<String> productIds): BigDecimal {
        return productIds.stream()
                .map(this::getProductPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
    }

    private fun getProductPrice(productId: String): BigDecimal {
        return BigDecimal("29.99")
    }
}