package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderItem
import com.example.order.entity.OrderStatus
import com.example.order.entity.Product
import com.example.order.repository.OrderRepository
import com.example.order.repository.ProductRepository
import com.example.order.repository.CustomerRepository
import com.example.order.exception.InvalidOrderException
import com.example.order.exception.ProductNotFoundException
import com.example.order.exception.CustomerNotFoundException
import com.example.order.exception.InsufficientStockException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import jakarta.validation.Valid

@Service
@Transactional
class OrderService(
    private val orderRepository: OrderRepository,
    private val productRepository: ProductRepository,
    private val customerRepository: CustomerRepository,
    private val inventoryService: InventoryService
) {

    fun createOrder(request: CreateOrderRequest): OrderResponse {
        validateOrderRequest(request)

        val customer = customerRepository.findById(request.customerId)
            .orElseThrow { CustomerNotFoundException("Customer not found: ${request.customerId}") }

        if (request.items.isEmpty()) {
            throw InvalidOrderException("Order must contain at least one item")
        }

        val productIds = request.items.map { it.productId }
        val products = productRepository.findByIdIn(productIds).associateBy { it.id }

        val order = Order(
            customerId = request.customerId,
            totalAmount = BigDecimal.ZERO,
            status = OrderStatus.PENDING
        )

        var totalAmount = BigDecimal.ZERO

        for (itemRequest in request.items) {
            val product = products[itemRequest.productId]
                ?: throw ProductNotFoundException("Product not found: ${itemRequest.productId}")

            checkStockAvailability(product, itemRequest.quantity)

            val subtotal = product.price.multiply(BigDecimal(itemRequest.quantity))
            totalAmount = totalAmount.add(subtotal)

            val orderItem = OrderItem(
                order = order,
                productId = product.id,
                quantity = itemRequest.quantity,
                priceAtPurchase = product.price,
                subtotal = subtotal
            )

            order.items.add(orderItem)
        }

        order.totalAmount = totalAmount

        val savedOrder = orderRepository.save(order)

        decrementStock(savedOrder)

        return convertToOrderResponse(savedOrder, products)
    }

    fun updateOrderItem(orderId: Long, itemId: Long, newQuantity: Int): OrderResponse {
        val order = orderRepository.findById(orderId)
            .orElseThrow { InvalidOrderException("Order not found: $orderId") }

        if (order.status != OrderStatus.PENDING) {
            throw InvalidOrderException("Cannot modify order in ${order.status} status")
        }

        val item = order.items.find { it.id == itemId }
            ?: throw InvalidOrderException("Order item not found: $itemId")

        val product = productRepository.findById(item.productId)
            .orElseThrow { ProductNotFoundException("Product not found: ${item.productId}") }

        val stockDifference = newQuantity - item.quantity

        if (stockDifference > 0) {
            checkStockAvailability(product, stockDifference)
        }

        item.quantity = newQuantity
        item.subtotal = product.price.multiply(BigDecimal(newQuantity))

        recalculateOrderTotal(order)

        val savedOrder = orderRepository.save(order)

        val products = productRepository.findByIdIn(order.items.map { it.productId })
            .associateBy { it.id }

        return convertToOrderResponse(savedOrder, products)
    }

    fun cancelOrder(orderId: Long): Boolean {
        val order = orderRepository.findById(orderId)
            .orElseThrow { InvalidOrderException("Order not found: $orderId") }

        if (order.status == OrderStatus.SHIPPED || order.status == OrderStatus.DELIVERED) {
            throw InvalidOrderException("Cannot cancel order in ${order.status} status")
        }

        order.status = OrderStatus.CANCELLED
        orderRepository.save(order)

        restoreStock(order)

        return true
    }

    private fun validateOrderRequest(request: CreateOrderRequest) {
        require(request.customerId > 0) { "Customer ID must be positive" }
        require(request.items.isNotEmpty()) { "Order must contain at least one item" }

        for (item in request.items) {
            require(item.productId > 0) { "Product ID must be positive" }
        }
    }

    private fun checkStockAvailability(product: Product, requestedQuantity: Int) {
        if (product.stockQuantity < requestedQuantity) {
            throw InsufficientStockException(
                "Insufficient stock for product ${product.id}. " +
                "Available: ${product.stockQuantity}, Requested: $requestedQuantity"
            )
        }
    }

    private fun decrementStock(order: Order) {
        for (item in order.items) {
            inventoryService.decrementStock(item.productId, item.quantity)
        }
    }

    private fun restoreStock(order: Order) {
        for (item in order.items) {
            inventoryService.incrementStock(item.productId, item.quantity)
        }
    }

    private fun recalculateOrderTotal(order: Order) {
        order.totalAmount = order.items
            .map { it.subtotal }
            .fold(BigDecimal.ZERO) { acc, subtotal -> acc.add(subtotal) }
    }

    private fun convertToOrderResponse(order: Order, products: Map<Long, Product>): OrderResponse {
        val itemDetails = order.items.map { item ->
            val product = products[item.productId]
            OrderItemDetail(
                itemId = item.id,
                productId = item.productId,
                productName = product?.name ?: "Unknown",
                quantity = item.quantity,
                priceAtPurchase = item.priceAtPurchase,
                subtotal = item.subtotal
            )
        }

        return OrderResponse(
            orderId = order.id,
            customerId = order.customerId,
            totalAmount = order.totalAmount,
            status = order.status,
            items = itemDetails,
            createdAt = order.createdAt
        )
    }

    fun getOrder(orderId: Long): OrderResponse {
        val order = orderRepository.findById(orderId)
            .orElseThrow { InvalidOrderException("Order not found: $orderId") }

        val products = productRepository.findByIdIn(order.items.map { it.productId })
            .associateBy { it.id }

        return convertToOrderResponse(order, products)
    }
}

data class CreateOrderRequest(
    val customerId: Long,
    val items: List<OrderItemRequest>
)

data class OrderItemRequest(
    val productId: Long,
    val quantity: Int
)

data class OrderResponse(
    val orderId: Long,
    val customerId: Long,
    val totalAmount: BigDecimal,
    val status: OrderStatus,
    val items: List<OrderItemDetail>,
    val createdAt: LocalDateTime
)

data class OrderItemDetail(
    val itemId: Long,
    val productId: Long,
    val productName: String,
    val quantity: Int,
    val priceAtPurchase: BigDecimal,
    val subtotal: BigDecimal
)

interface InventoryService {
    fun decrementStock(productId: Long, quantity: Int)
    fun incrementStock(productId: Long, quantity: Int)
}
