package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

@Service
@Transactional
class PartialCancellationService(
    private val orderRepository: OrderRepository,
    private val orderItemRepository: OrderItemRepository,
    private val stockService: StockService
) {

    fun cancelOrderItem(orderId: Long, itemId: Long): CancellationResult {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        validateCancellation(order)

        val item = order.items.find { it.id == itemId }
            ?: throw IllegalArgumentException("Item not found: $itemId")

        if (item.status == ItemStatus.CANCELLED) {
            throw IllegalStateException("Item already cancelled")
        }

        val activeItems = order.items.filter { it.status == ItemStatus.ACTIVE }
        if (activeItems.size <= 1) {
            throw IllegalStateException("Cannot cancel last item. Cancel entire order instead.")
        }

        item.status = ItemStatus.CANCELLED

        stockService.restoreStock(item.productId, item.quantity)

        orderItemRepository.save(item)
        orderRepository.save(order)

        return CancellationResult(
            orderId = orderId,
            cancelledItemId = itemId,
            refundAmount = item.subtotal,
            newOrderTotal = order.totalAmount,
            success = true
        )
    }

    private fun validateCancellation(order: Order) {
        if (order.status == OrderStatus.SHIPPED || order.status == OrderStatus.DELIVERED) {
            throw IllegalStateException("Cannot cancel items from shipped order")
        }
    }

    fun cancelMultipleItems(orderId: Long, itemIds: List<Long>): List<CancellationResult> {
        return itemIds.map { cancelOrderItem(orderId, it) }
    }
}

data class CancellationResult(
    val orderId: Long,
    val cancelledItemId: Long,
    val refundAmount: BigDecimal,
    val newOrderTotal: BigDecimal,
    val success: Boolean
)

data class Order(
    val id: Long = 0,
    val customerId: Long,
    var subtotal: BigDecimal,
    var discountAmount: BigDecimal = BigDecimal.ZERO,
    var shippingFee: BigDecimal = BigDecimal.ZERO,
    var totalAmount: BigDecimal,
    var status: OrderStatus,
    val items: MutableList<OrderItem> = mutableListOf()
)

data class OrderItem(
    val id: Long = 0,
    val orderId: Long,
    val productId: Long,
    var quantity: Int,
    val unitPrice: BigDecimal,
    var subtotal: BigDecimal,
    var status: ItemStatus = ItemStatus.ACTIVE
)

enum class OrderStatus {
    PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
}

enum class ItemStatus {
    ACTIVE, CANCELLED
}

interface OrderRepository {
    fun findById(id: Long): java.util.Optional<Order>
    fun save(order: Order): Order
}

interface OrderItemRepository {
    fun save(item: OrderItem): OrderItem
}

interface StockService {
    fun restoreStock(productId: Long, quantity: Int)
}
