package com.example.checkout.service

import com.example.checkout.entity.Cart
import com.example.checkout.entity.Order
import com.example.checkout.entity.OrderItem
import com.example.checkout.entity.OrderStatus
import com.example.checkout.repository.CartRepository
import com.example.checkout.repository.OrderRepository
import com.example.checkout.repository.ProductRepository
import com.example.checkout.exception.CartNotFoundException
import com.example.checkout.exception.CheckoutException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
@Transactional
class CheckoutService(
    private val cartRepository: CartRepository,
    private val orderRepository: OrderRepository,
    private val productRepository: ProductRepository,
    private val paymentService: PaymentService,
    private val notificationService: NotificationService
) {

    fun processCheckout(cartId: Long, customerId: Long): CheckoutResult {
        val cart = findCart(cartId, customerId)

        if (cart.items.isEmpty()) {
            throw CheckoutException("Cannot checkout empty cart")
        }

        val order = createOrderFromCart(cart)
        val savedOrder = orderRepository.save(order)

        decrementStockForOrder(savedOrder)

        try {
            val paymentResult = paymentService.processPayment(
                orderId = savedOrder.id,
                amount = savedOrder.totalAmount,
                customerId = customerId
            )

            if (paymentResult.success) {
                savedOrder.status = OrderStatus.CONFIRMED
                notificationService.sendOrderConfirmation(savedOrder.id, customerId)
                clearCart(cart)
            } else {
                savedOrder.status = OrderStatus.CANCELLED
                restoreStockForOrder(savedOrder)
                throw CheckoutException("Payment failed: ${paymentResult.message}")
            }
        } catch (e: Exception) {
            savedOrder.status = OrderStatus.CANCELLED
            restoreStockForOrder(savedOrder)
            throw CheckoutException("Checkout failed: ${e.message}", e)
        }

        return CheckoutResult(
            orderId = savedOrder.id,
            orderTotal = savedOrder.totalAmount,
            success = true
        )
    }

    private fun findCart(cartId: Long, customerId: Long): Cart {
        val cart = cartRepository.findById(cartId)
            .orElseThrow { CartNotFoundException("Cart not found: $cartId") }

        if (cart.customerId != customerId) {
            throw CheckoutException("Cart does not belong to customer")
        }

        return cart
    }

    private fun createOrderFromCart(cart: Cart): Order {
        val productIds = cart.items.map { it.productId }
        val products = productRepository.findByIdIn(productIds).associateBy { it.id }

        val order = Order(
            customerId = cart.customerId,
            totalAmount = BigDecimal.ZERO,
            status = OrderStatus.PENDING
        )

        var total = BigDecimal.ZERO

        for (cartItem in cart.items) {
            val product = products[cartItem.productId]
                ?: throw CheckoutException("Product not found: ${cartItem.productId}")

            val itemTotal = product.price.multiply(BigDecimal(cartItem.quantity))
            total = total.add(itemTotal)

            val orderItem = OrderItem(
                order = order,
                productId = product.id,
                quantity = cartItem.quantity,
                priceAtPurchase = product.price
            )

            order.items.add(orderItem)
        }

        order.totalAmount = total
        return order
    }

    private fun decrementStockForOrder(order: Order) {
        for (item in order.items) {
            val product = productRepository.findById(item.productId)
                .orElseThrow { CheckoutException("Product not found: ${item.productId}") }

            if (product.stockQuantity >= item.quantity) {
                product.stockQuantity -= item.quantity
                productRepository.save(product)
            } else {
                throw CheckoutException(
                    "Insufficient stock for product ${item.productId}. " +
                    "Available: ${product.stockQuantity}, Requested: ${item.quantity}"
                )
            }
        }
    }

    private fun restoreStockForOrder(order: Order) {
        for (item in order.items) {
            val product = productRepository.findById(item.productId).orElse(null) ?: continue
            product.stockQuantity += item.quantity
            productRepository.save(product)
        }
    }

    private fun clearCart(cart: Cart) {
        cart.items.clear()
        cartRepository.save(cart)
    }

    fun getOrderSummary(orderId: Long): OrderSummary {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val productIds = order.items.map { it.productId }
        val products = productRepository.findByIdIn(productIds).associateBy { it.id }

        val itemSummaries = order.items.map { item ->
            val product = products[item.productId]
            OrderItemSummary(
                productId = item.productId,
                productName = product?.name ?: "Unknown",
                quantity = item.quantity,
                priceAtPurchase = item.priceAtPurchase,
                subtotal = item.priceAtPurchase.multiply(BigDecimal(item.quantity))
            )
        }

        return OrderSummary(
            orderId = order.id,
            customerId = order.customerId,
            items = itemSummaries,
            totalAmount = order.totalAmount,
            status = order.status,
            createdAt = order.createdAt
        )
    }
}

data class CheckoutResult(
    val orderId: Long,
    val orderTotal: BigDecimal,
    val success: Boolean,
    val message: String? = null
)

data class OrderSummary(
    val orderId: Long,
    val customerId: Long,
    val items: List<OrderItemSummary>,
    val totalAmount: BigDecimal,
    val status: OrderStatus,
    val createdAt: LocalDateTime
)

data class OrderItemSummary(
    val productId: Long,
    val productName: String,
    val quantity: Int,
    val priceAtPurchase: BigDecimal,
    val subtotal: BigDecimal
)

interface PaymentService {
    fun processPayment(orderId: Long, amount: BigDecimal, customerId: Long): PaymentResult
}

data class PaymentResult(
    val success: Boolean,
    val transactionId: String? = null,
    val message: String? = null
)

interface NotificationService {
    fun sendOrderConfirmation(orderId: Long, customerId: Long)
}
