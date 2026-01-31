package com.example.ecommerce.service

import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.OrderStatus
import com.example.ecommerce.entity.User
import com.example.ecommerce.exception.OrderNotFoundException
import com.example.ecommerce.exception.UnauthorizedException
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.UserRepository
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
@Transactional(readOnly = true)
class OrderService(
    private val orderRepository: OrderRepository,
    private val userRepository: UserRepository
) {

    fun getOrderById(orderId: Long, currentUserId: Long): Order {
        validateUserExists(currentUserId)
        
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order with ID $orderId not found") }
        
        return enrichOrderWithCalculations(order)
    }

    fun getUserOrders(userId: Long, currentUserId: Long, pageable: Pageable): Page<Order> {
        validateUserAccess(userId, currentUserId)
        
        return orderRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable)
            .map { enrichOrderWithCalculations(it) }
    }

    fun getOrdersByStatus(status: OrderStatus, currentUserId: Long, pageable: Pageable): Page<Order> {
        validateUserExists(currentUserId)
        
        return orderRepository.findByUserIdAndStatusOrderByCreatedAtDesc(currentUserId, status, pageable)
            .map { enrichOrderWithCalculations(it) }
    }

    @Transactional
    fun cancelOrder(orderId: Long, currentUserId: Long): Order {
        val order = getOrderById(orderId, currentUserId)
        
        validateOrderCancellation(order)
        
        return order.copy(
            status = OrderStatus.CANCELLED,
            updatedAt = LocalDateTime.now()
        ).also { orderRepository.save(it) }
    }

    fun calculateOrderTotal(orderId: Long, currentUserId: Long): BigDecimal {
        val order = getOrderById(orderId, currentUserId)
        return calculateTotalAmount(order)
    }

    private fun validateUserExists(userId: Long) {
        if (!userRepository.existsById(userId)) {
            throw UnauthorizedException("User not found")
        }
    }

    private fun validateUserAccess(targetUserId: Long, currentUserId: Long) {
        if (targetUserId != currentUserId) {
            throw UnauthorizedException("Access denied to user orders")
        }
    }

    private fun validateOrderCancellation(order: Order) {
        when (order.status) {
            OrderStatus.DELIVERED, OrderStatus.CANCELLED -> 
                throw IllegalStateException("Cannot cancel order in ${order.status} status")
            OrderStatus.SHIPPED -> 
                throw IllegalStateException("Cannot cancel shipped order")
            else -> Unit
        }
    }

    private fun enrichOrderWithCalculations(order: Order): Order {
        val totalAmount = calculateTotalAmount(order)
        val taxAmount = calculateTaxAmount(totalAmount)
        
        return order.copy(
            totalAmount = totalAmount,
            taxAmount = taxAmount,
            finalAmount = totalAmount.add(taxAmount)
        )
    }

    private fun calculateTotalAmount(order: Order): BigDecimal {
        return order.orderItems.sumOf { item ->
            item.price.multiply(BigDecimal.valueOf(item.quantity.toLong()))
        }
    }

    private fun calculateTaxAmount(totalAmount: BigDecimal): BigDecimal {
        val taxRate = BigDecimal("0.08")
        return totalAmount.multiply(taxRate).setScale(2, BigDecimal.ROUND_HALF_UP)
    }
}