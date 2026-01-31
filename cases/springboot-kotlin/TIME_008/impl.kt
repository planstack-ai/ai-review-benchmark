package com.example.order.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime
import java.util.*

@Service
@Transactional
class OrderManagementService(
    private val orderRepository: OrderRepository,
    private val customerRepository: CustomerRepository,
    private val orderItemRepository: OrderItemRepository,
    private val productService: ProductService
) {

    @Transactional
    fun createOrder(request: CreateOrderRequest): Order {
        val customer = customerRepository.findById(request.customerId)
            .orElseThrow { IllegalArgumentException("Customer not found: ${request.customerId}") }

        if (request.items.isEmpty()) {
            throw IllegalArgumentException("Order must contain at least one item")
        }

        if (request.deliveryAddress.isBlank()) {
            throw IllegalArgumentException("Delivery address is required")
        }

        val orderNumber = generateOrderNumber()
        val totalAmount = calculateTotalAmount(request.items)

        val order = Order(
            customerId = request.customerId,
            orderNumber = orderNumber,
            orderDate = LocalDate.now(),
            deliveryDate = request.deliveryDate,
            deliveryAddress = request.deliveryAddress,
            totalAmount = totalAmount,
            status = OrderStatus.PENDING,
            createdAt = LocalDateTime.now(),
            updatedAt = LocalDateTime.now()
        )

        val savedOrder = orderRepository.save(order)

        request.items.forEach { itemRequest ->
            val product = productService.getProduct(itemRequest.productId)
            val orderItem = OrderItem(
                orderId = savedOrder.id,
                productId = itemRequest.productId,
                quantity = itemRequest.quantity,
                unitPrice = product.price
            )
            orderItemRepository.save(orderItem)
        }

        return savedOrder
    }

    @Transactional
    fun updateDeliveryDate(orderId: Long, newDeliveryDate: LocalDate): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        if (order.status == OrderStatus.SHIPPED || order.status == OrderStatus.DELIVERED) {
            throw IllegalStateException("Cannot update delivery date for order in ${order.status} status")
        }

        val updatedOrder = order.copy(
            deliveryDate = newDeliveryDate,
            updatedAt = LocalDateTime.now()
        )

        return orderRepository.save(updatedOrder)
    }

    fun getOrdersByDeliveryDate(date: LocalDate): List<OrderSummary> {
        return orderRepository.findByDeliveryDate(date)
            .map { order ->
                val items = orderItemRepository.findByOrderId(order.id)
                OrderSummary(
                    orderId = order.id,
                    orderNumber = order.orderNumber,
                    customerId = order.customerId,
                    deliveryDate = order.deliveryDate,
                    deliveryAddress = order.deliveryAddress,
                    totalAmount = order.totalAmount,
                    status = order.status,
                    itemCount = items.size
                )
            }
            .sortedBy { it.orderNumber }
    }

    fun getCustomerOrders(customerId: Long): List<OrderSummary> {
        val customer = customerRepository.findById(customerId)
            .orElseThrow { IllegalArgumentException("Customer not found: $customerId") }

        return orderRepository.findByCustomerId(customerId)
            .map { order ->
                val items = orderItemRepository.findByOrderId(order.id)
                OrderSummary(
                    orderId = order.id,
                    orderNumber = order.orderNumber,
                    customerId = order.customerId,
                    deliveryDate = order.deliveryDate,
                    deliveryAddress = order.deliveryAddress,
                    totalAmount = order.totalAmount,
                    status = order.status,
                    itemCount = items.size
                )
            }
            .sortedByDescending { it.orderId }
    }

    @Transactional
    fun cancelOrder(orderId: Long, reason: String): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        if (order.status == OrderStatus.DELIVERED) {
            throw IllegalStateException("Cannot cancel delivered order")
        }

        if (order.status == OrderStatus.CANCELLED) {
            throw IllegalStateException("Order is already cancelled")
        }

        val updatedOrder = order.copy(
            status = OrderStatus.CANCELLED,
            updatedAt = LocalDateTime.now()
        )

        return orderRepository.save(updatedOrder)
    }

    private fun generateOrderNumber(): String {
        val timestamp = System.currentTimeMillis()
        val random = Random().nextInt(9999)
        return "ORD${timestamp}${random.toString().padStart(4, '0')}"
    }

    private fun calculateTotalAmount(items: List<OrderItemRequest>): BigDecimal {
        var total = BigDecimal.ZERO

        items.forEach { itemRequest ->
            val product = productService.getProduct(itemRequest.productId)
            val itemTotal = product.price.multiply(BigDecimal(itemRequest.quantity))
            total = total.add(itemTotal)
        }

        return total
    }

    fun getUpcomingDeliveries(daysAhead: Int): List<OrderSummary> {
        val startDate = LocalDate.now()
        val endDate = startDate.plusDays(daysAhead.toLong())

        return orderRepository.findAll()
            .filter { order ->
                !order.deliveryDate.isBefore(startDate) && !order.deliveryDate.isAfter(endDate)
            }
            .filter { order ->
                order.status != OrderStatus.CANCELLED && order.status != OrderStatus.DELIVERED
            }
            .map { order ->
                val items = orderItemRepository.findByOrderId(order.id)
                OrderSummary(
                    orderId = order.id,
                    orderNumber = order.orderNumber,
                    customerId = order.customerId,
                    deliveryDate = order.deliveryDate,
                    deliveryAddress = order.deliveryAddress,
                    totalAmount = order.totalAmount,
                    status = order.status,
                    itemCount = items.size
                )
            }
            .sortedBy { it.deliveryDate }
    }
}

data class OrderSummary(
    val orderId: Long,
    val orderNumber: String,
    val customerId: Long,
    val deliveryDate: LocalDate,
    val deliveryAddress: String,
    val totalAmount: BigDecimal,
    val status: OrderStatus,
    val itemCount: Int
)

data class Product(
    val id: Long,
    val name: String,
    val price: BigDecimal
)

interface ProductService {
    fun getProduct(productId: Long): Product
}
