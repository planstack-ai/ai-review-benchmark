package com.example.order.service

import com.example.order.entity.Order
import com.example.order.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

data class ExternalOrderRequest(
    val externalId: String,
    val customerEmail: String,
    val totalAmount: BigDecimal
)

@Service
class ExternalOrderService(
    private val orderRepository: OrderRepository
) {

    @Transactional
    fun findOrCreateOrder(request: ExternalOrderRequest): Order {
        // BUG: Race condition between check and insert
        // If two threads execute this simultaneously with same externalId:
        // 1. Both threads check and find no existing order
        // 2. Both threads proceed to create new order
        // 3. Two duplicate orders are created in the database
        //
        // This is a classic "check-then-act" race condition
        val existing = orderRepository.findByExternalId(request.externalId)
        return if (existing != null) {
            existing
        } else {
            val order = Order(
                externalId = request.externalId,
                customerEmail = request.customerEmail,
                totalAmount = request.totalAmount,
                status = "PENDING"
            )
            orderRepository.save(order)
        }
    }

    fun processExternalOrder(request: ExternalOrderRequest): OrderResult {
        val order = findOrCreateOrder(request)

        return OrderResult(
            orderId = order.id!!,
            externalId = order.externalId,
            status = order.status,
            isNewOrder = order.createdAt.isAfter(
                java.time.LocalDateTime.now().minusSeconds(1)
            )
        )
    }
}

data class OrderResult(
    val orderId: Long,
    val externalId: String,
    val status: String,
    val isNewOrder: Boolean
)
