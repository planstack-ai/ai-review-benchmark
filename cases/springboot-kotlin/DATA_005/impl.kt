package com.example.ecommerce.service

import com.example.ecommerce.dto.OrderDetailDto
import com.example.ecommerce.dto.OrderItemDetailDto
import com.example.ecommerce.entity.Order
import com.example.ecommerce.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class OrderDetailService(
    private val orderRepository: OrderRepository
) {
    @Transactional(readOnly = true)
    fun getOrderDetails(orderId: Long): OrderDetailDto {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val itemDetails = order.items.map { item ->
            OrderItemDetailDto(
                productId = item.productId,
                productName = item.product.name,
                unitPrice = item.product.priceCents,
                quantity = item.quantity,
                lineTotal = item.product.priceCents * item.quantity
            )
        }

        return OrderDetailDto(
            orderId = order.id!!,
            status = order.status,
            createdAt = order.createdAt,
            items = itemDetails,
            totalAmount = calculateTotal(order)
        )
    }

    @Transactional(readOnly = true)
    fun getOrderHistory(userId: Long): List<OrderDetailDto> {
        val orders = orderRepository.findByUserIdOrderByCreatedAtDesc(userId)

        return orders.map { order ->
            val items = order.items.map { item ->
                OrderItemDetailDto(
                    productId = item.productId,
                    productName = item.product.name,
                    unitPrice = item.product.priceCents,
                    quantity = item.quantity,
                    lineTotal = item.product.priceCents * item.quantity
                )
            }

            OrderDetailDto(
                orderId = order.id!!,
                status = order.status,
                createdAt = order.createdAt,
                items = items,
                totalAmount = calculateTotal(order)
            )
        }
    }

    @Transactional(readOnly = true)
    fun generateInvoice(orderId: Long): ByteArray {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        val invoice = buildString {
            appendLine("INVOICE")
            appendLine("Order #: ${order.id}")
            appendLine("Date: ${order.createdAt}")
            appendLine()
            appendLine("Items:")

            order.items.forEach { item ->
                appendLine("- ${item.product.name} x${item.quantity} @ $${item.product.priceCents / 100.0} = $${(item.product.priceCents * item.quantity) / 100.0}")
            }

            appendLine()
            appendLine("Total: $${calculateTotal(order) / 100.0}")
        }

        return invoice.toByteArray()
    }

    private fun calculateTotal(order: Order): Long {
        return order.items.sumOf { item ->
            item.product.priceCents.toLong() * item.quantity
        }
    }
}

data class OrderDetailDto(
    val orderId: Long,
    val status: String,
    val createdAt: java.time.LocalDateTime,
    val items: List<OrderItemDetailDto>,
    val totalAmount: Long
)

data class OrderItemDetailDto(
    val productId: Long,
    val productName: String,
    val unitPrice: Int,
    val quantity: Int,
    val lineTotal: Int
)
