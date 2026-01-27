package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.Payment
import com.example.order.entity.PaymentStatus
import com.example.order.exception.OrderNotFoundException
import com.example.order.exception.PaymentException
import com.example.order.repository.OrderRepository
import com.example.order.repository.PaymentRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Propagation
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
class OrderProcessingService(
    private val orderRepository: OrderRepository,
    private val paymentService: PaymentService,
    private val paymentRepository: PaymentRepository
) {
    // BUG: @Transactional propagation issue
    // This method has REQUIRED propagation (default), but paymentService.processPayment
    // uses REQUIRES_NEW, causing partial commit if payment succeeds but order update fails
    @Transactional
    fun processOrderWithPayment(orderId: Long, paymentAmount: BigDecimal): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        // Update order status
        order.status = "PROCESSING"
        order.processedAt = LocalDateTime.now()
        orderRepository.save(order)

        // Process payment - this runs in a SEPARATE transaction (REQUIRES_NEW)
        // If this succeeds but later code fails, payment is committed but order is rolled back
        val payment = paymentService.processPayment(orderId, paymentAmount)

        // This could fail after payment is already committed
        order.paymentId = payment.id
        order.status = "PAID"

        return orderRepository.save(order)
    }

    @Transactional(readOnly = true)
    fun getOrderWithPayment(orderId: Long): OrderWithPayment {
        val order = orderRepository.findById(orderId)
            .orElseThrow { OrderNotFoundException("Order not found: $orderId") }

        val payment = order.paymentId?.let {
            paymentRepository.findById(it).orElse(null)
        }

        return OrderWithPayment(order, payment)
    }

    data class OrderWithPayment(
        val order: Order,
        val payment: Payment?
    )
}

@Service
class PaymentService(
    private val paymentRepository: PaymentRepository
) {
    // This method has REQUIRES_NEW - runs in a separate transaction
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun processPayment(orderId: Long, amount: BigDecimal): Payment {
        val payment = Payment(
            orderId = orderId,
            amount = amount,
            status = PaymentStatus.PENDING,
            createdAt = LocalDateTime.now()
        )

        // Simulate payment processing
        payment.status = PaymentStatus.COMPLETED
        payment.processedAt = LocalDateTime.now()

        return paymentRepository.save(payment)
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun refundPayment(paymentId: Long): Payment {
        val payment = paymentRepository.findById(paymentId)
            .orElseThrow { PaymentException("Payment not found: $paymentId") }

        payment.status = PaymentStatus.REFUNDED
        payment.refundedAt = LocalDateTime.now()

        return paymentRepository.save(payment)
    }
}
