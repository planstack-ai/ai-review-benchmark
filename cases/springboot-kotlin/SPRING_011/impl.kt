package com.example.order.entity

import jakarta.persistence.*
import java.math.BigDecimal
import java.time.LocalDateTime

@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "customer_id", nullable = false)
    val customerId: Long,

    @Column(name = "total_amount", nullable = false)
    var totalAmount: BigDecimal,

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    var status: OrderStatus = OrderStatus.PENDING,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @OneToMany(mappedBy = "order")
    val items: MutableList<OrderItem> = mutableListOf()
) {
    fun addItem(orderItem: OrderItem) {
        items.add(orderItem)
        recalculateTotal()
    }

    fun removeItem(orderItem: OrderItem) {
        items.remove(orderItem)
        recalculateTotal()
    }

    private fun recalculateTotal() {
        totalAmount = items.sumOf { it.subtotal }
    }
}

@Entity
@Table(name = "order_items")
data class OrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    var order: Order,

    @Column(name = "product_id", nullable = false)
    val productId: Long,

    @Column(name = "product_name", nullable = false)
    val productName: String,

    @Column(nullable = false)
    val quantity: Int,

    @Column(name = "unit_price", nullable = false)
    val unitPrice: BigDecimal,

    @Column(nullable = false)
    val subtotal: BigDecimal
) {
    init {
        require(quantity > 0) { "Quantity must be positive" }
        require(unitPrice > BigDecimal.ZERO) { "Unit price must be positive" }
    }
}

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

// Service to demonstrate the issue
@Service
class OrderManagementService(
    private val orderRepository: OrderRepository,
    private val orderItemRepository: OrderItemRepository
) {

    @Transactional
    fun createOrder(customerId: Long, items: List<OrderItemRequest>): Order {
        val order = Order(
            customerId = customerId,
            totalAmount = BigDecimal.ZERO
        )

        val savedOrder = orderRepository.save(order)

        items.forEach { itemRequest ->
            val subtotal = itemRequest.unitPrice.multiply(BigDecimal(itemRequest.quantity))
            val orderItem = OrderItem(
                order = savedOrder,
                productId = itemRequest.productId,
                productName = itemRequest.productName,
                quantity = itemRequest.quantity,
                unitPrice = itemRequest.unitPrice,
                subtotal = subtotal
            )
            savedOrder.addItem(orderItem)
            orderItemRepository.save(orderItem)
        }

        return orderRepository.save(savedOrder)
    }

    @Transactional
    fun deleteOrder(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        // Simply delete the order - but orphan removal is not configured
        // This will leave orphaned order_items in the database
        orderRepository.delete(order)
    }

    @Transactional
    fun cancelOrder(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        order.status = OrderStatus.CANCELLED
        orderRepository.save(order)
    }

    fun getOrder(orderId: Long): Order {
        return orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }
    }
}

data class OrderItemRequest(
    val productId: Long,
    val productName: String,
    val quantity: Int,
    val unitPrice: BigDecimal
)
