package com.example.order.service

import com.example.order.entity.Order
import com.example.order.repository.OrderRepository
import org.springframework.data.jpa.repository.EntityGraph
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.stereotype.Repository
import org.springframework.stereotype.Service
import java.util.*

@Repository
interface OrderRepository : JpaRepository<Order, Long> {

    // BUG: @EntityGraph with multiple collection paths causes cartesian product
    // When fetching: items (collection) AND payments (collection)
    // SQL generates: ORDER × ORDER_ITEMS × PAYMENTS
    //
    // Example with 1 order, 4 items, 3 payments:
    // - Returns 4 × 3 = 12 rows from database
    // - Order data duplicated 12 times
    // - OrderItem data duplicated 3 times each
    // - Payment data duplicated 4 times each
    //
    // For orders with many items and payments:
    // - 10 items × 5 payments = 50 rows (massive data duplication)
    // - Network bandwidth waste
    // - Memory overhead
    // - Hibernate has to de-duplicate rows
    //
    // Solution: Use separate queries or fetch collections in separate EntityGraphs
    @EntityGraph(attributePaths = ["items", "items.product", "payments"])
    override fun findById(id: Long): Optional<Order>
}

@Service
class OrderDetailService(
    private val orderRepository: OrderRepository
) {

    fun getOrderWithDetails(orderId: Long): OrderDetailView {
        val order = orderRepository.findById(orderId)
            .orElseThrow { NoSuchElementException("Order not found: $orderId") }

        return OrderDetailView(
            orderId = order.id!!,
            customerEmail = order.customerEmail,
            totalAmount = order.totalAmount,
            status = order.status,
            itemCount = order.items.size,
            paymentCount = order.payments.size,
            items = order.items.map { item ->
                OrderItemView(
                    productName = item.product.name,
                    quantity = item.quantity,
                    price = item.price
                )
            },
            payments = order.payments.map { payment ->
                PaymentView(
                    amount = payment.amount,
                    method = payment.paymentMethod,
                    date = payment.paymentDate
                )
            }
        )
    }
}

data class OrderDetailView(
    val orderId: Long,
    val customerEmail: String,
    val totalAmount: java.math.BigDecimal,
    val status: String,
    val itemCount: Int,
    val paymentCount: Int,
    val items: List<OrderItemView>,
    val payments: List<PaymentView>
)

data class OrderItemView(
    val productName: String,
    val quantity: Int,
    val price: java.math.BigDecimal
)

data class PaymentView(
    val amount: java.math.BigDecimal,
    val method: String,
    val date: java.time.LocalDateTime
)
