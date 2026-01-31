package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

@Service
@Transactional
class BulkOrderCalculationService(
    private val bulkOrderRepository: BulkOrderRepository,
    private val productRepository: ProductRepository
) {

    fun calculateOrderTotal(orderId: Long): OrderCalculationResult {
        val order = bulkOrderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val itemTotals = order.items.map { item ->
            calculateLineTotal(item)
        }

        val totalAmount = itemTotals.fold(BigDecimal.ZERO) { acc, total -> acc.add(total) }

        order.totalAmount = totalAmount
        bulkOrderRepository.save(order)

        return OrderCalculationResult(
            orderId = orderId,
            itemCount = order.items.size,
            totalAmount = totalAmount
        )
    }

    fun createBulkOrder(customerId: Long, items: List<BulkOrderItemRequest>): BulkOrder {
        val order = BulkOrder(
            customerId = customerId,
            status = OrderStatus.DRAFT
        )

        var totalAmount = BigDecimal.ZERO

        items.forEach { itemRequest ->
            val product = productRepository.findById(itemRequest.productId)
                .orElseThrow { IllegalArgumentException("Product not found: ${itemRequest.productId}") }

            val lineTotal = calculateLineTotalFromRequest(product.unitPrice, itemRequest.quantity)

            val orderItem = BulkOrderItem(
                orderId = order.id,
                productId = product.id,
                productName = product.name,
                unitPrice = product.unitPrice,
                quantity = itemRequest.quantity,
                lineTotal = lineTotal
            )

            order.items.add(orderItem)
            totalAmount = totalAmount.add(lineTotal)
        }

        order.totalAmount = totalAmount
        return bulkOrderRepository.save(order)
    }

    private fun calculateLineTotal(item: BulkOrderItem): BigDecimal {
        val total = item.unitPrice * item.quantity
        return BigDecimal(total)
    }

    private fun calculateLineTotalFromRequest(unitPrice: Int, quantity: Int): BigDecimal {
        val total = unitPrice * quantity
        return BigDecimal(total)
    }
}

data class OrderCalculationResult(
    val orderId: Long,
    val itemCount: Int,
    val totalAmount: BigDecimal
)

data class BulkOrderItemRequest(
    val productId: Long,
    val quantity: Int
)

data class BulkOrder(
    val id: Long = 0,
    val customerId: Long,
    val orderType: String = "BULK",
    var totalAmount: BigDecimal = BigDecimal.ZERO,
    var status: OrderStatus,
    val items: MutableList<BulkOrderItem> = mutableListOf()
)

data class BulkOrderItem(
    val id: Long = 0,
    val orderId: Long,
    val productId: Long,
    val productName: String,
    val unitPrice: Int,
    val quantity: Int,
    var lineTotal: BigDecimal = BigDecimal.ZERO
)

data class Product(
    val id: Long = 0,
    val name: String,
    val unitPrice: Int,
    val stockQuantity: Int
)

enum class OrderStatus {
    DRAFT, PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
}

interface BulkOrderRepository {
    fun findById(id: Long): java.util.Optional<BulkOrder>
    fun save(order: BulkOrder): BulkOrder
}

interface ProductRepository {
    fun findById(id: Long): java.util.Optional<Product>
}
