package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderItem
import com.example.order.repository.OrderRepository
import org.springframework.scheduling.annotation.Async
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

data class CreateOrderRequest(
    val customerEmail: String,
    val items: List<OrderItemRequest>
)

data class OrderItemRequest(
    val productName: String,
    val quantity: Int,
    val price: BigDecimal
)

@Service
class OrderService(
    private val orderRepository: OrderRepository,
    private val emailService: EmailService
) {

    @Transactional
    fun createOrder(request: CreateOrderRequest): Order {
        val totalAmount = request.items.sumOf { it.price * it.quantity.toBigDecimal() }

        val order = Order(
            customerEmail = request.customerEmail,
            totalAmount = totalAmount,
            status = "PENDING"
        )

        request.items.forEach { itemRequest ->
            val orderItem = OrderItem(
                order = order,
                productName = itemRequest.productName,
                quantity = itemRequest.quantity,
                price = itemRequest.price
            )
            order.items.add(orderItem)
        }

        val savedOrder = orderRepository.save(order)

        // BUG: @Async method called inside transaction
        // The notification may be sent before the transaction commits
        // If transaction fails, notification already sent with uncommitted data
        sendOrderConfirmation(savedOrder.id!!)

        return savedOrder
    }

    @Async
    fun sendOrderConfirmation(orderId: Long) {
        // This may execute before the transaction commits
        // The order might not be visible to other transactions yet
        val order = orderRepository.findById(orderId).orElseThrow()
        emailService.sendOrderConfirmation(
            orderId = order.id!!,
            customerEmail = order.customerEmail,
            totalAmount = order.totalAmount
        )
    }
}

interface EmailService {
    fun sendOrderConfirmation(orderId: Long, customerEmail: String, totalAmount: BigDecimal)
}
