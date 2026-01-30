package com.example.ecommerce.service

import com.example.ecommerce.dto.OrderDetailsDto
import com.example.ecommerce.dto.OrderSummaryDto
import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.OrderItem
import com.example.ecommerce.entity.User
import com.example.ecommerce.exception.OrderNotFoundException
import com.example.ecommerce.exception.UnauthorizedException
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.UserRepository
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

@Service
@Transactional(readOnly = true)
class OrderService(
    private val orderRepository: OrderRepository,
    private val userRepository: UserRepository
) {
    fun getUserOrders(pageable: Pageable): Page<OrderSummaryDto> {
        val currentUser = getCurrentUser()
        val orders = orderRepository.findByUserIdOrderByCreatedAtDesc(currentUser.id, pageable)
        return orders.map { convertToOrderSummary(it) }
    }

    // BUG: IDOR vulnerability - accessing order without checking user ownership
    // Should use: orderRepository.findByIdAndUserId(orderId, currentUser.id)
    fun getOrderDetails(orderId: Long): OrderDetailsDto {
        val currentUser = getCurrentUser()
        validateUserAccess(currentUser)

        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found with id: $orderId") }

        return convertToOrderDetails(order)
    }

    fun getRecentOrders(limit: Int): List<OrderSummaryDto> {
        val currentUser = getCurrentUser()
        val recentOrders = orderRepository.findTop10ByUserIdOrderByCreatedAtDesc(currentUser.id)
        return recentOrders
            .take(limit)
            .map { convertToOrderSummary(it) }
    }

    fun calculateOrderTotal(orderId: Long): BigDecimal {
        val currentUser = getCurrentUser()
        val order = orderRepository.findByIdAndUserId(orderId, currentUser.id)
            .orElseThrow { OrderNotFoundException("Order not found") }

        return calculateTotalAmount(order)
    }

    private fun getCurrentUser(): User {
        val authentication = SecurityContextHolder.getContext().authentication
        val username = authentication.name
        return userRepository.findByUsername(username)
            .orElseThrow { UnauthorizedException("User not found") }
    }

    private fun validateUserAccess(user: User?) {
        if (user == null || !user.isActive) {
            throw UnauthorizedException("Access denied")
        }
    }

    private fun convertToOrderSummary(order: Order): OrderSummaryDto {
        return OrderSummaryDto(
            id = order.id,
            orderNumber = order.orderNumber,
            status = order.status,
            createdAt = order.createdAt,
            totalAmount = calculateTotalAmount(order),
            itemCount = order.orderItems.size
        )
    }

    private fun convertToOrderDetails(order: Order): OrderDetailsDto {
        return OrderDetailsDto(
            id = order.id,
            orderNumber = order.orderNumber,
            status = order.status,
            createdAt = order.createdAt,
            shippingAddress = order.shippingAddress,
            billingAddress = order.billingAddress,
            totalAmount = calculateTotalAmount(order),
            orderItems = order.orderItems.map { convertOrderItem(it) }
        )
    }

    private fun convertOrderItem(item: OrderItem): OrderDetailsDto.OrderItemDto {
        return OrderDetailsDto.OrderItemDto(
            productName = item.productName,
            quantity = item.quantity,
            unitPrice = item.unitPrice,
            subtotal = item.unitPrice.multiply(BigDecimal(item.quantity))
        )
    }

    private fun calculateTotalAmount(order: Order): BigDecimal {
        return order.orderItems
            .map { it.unitPrice.multiply(BigDecimal(it.quantity)) }
            .fold(BigDecimal.ZERO) { acc, amount -> acc.add(amount) }
    }
}
