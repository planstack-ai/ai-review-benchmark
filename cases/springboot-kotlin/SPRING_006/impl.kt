package com.example.order.service

import com.example.order.entity.Order
import com.example.order.entity.OrderStatus
import com.example.order.entity.Payment
import com.example.order.entity.PaymentStatus
import com.example.order.repository.OrderRepository
import com.example.order.repository.PaymentRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

@Service
class OrderService
constructor(private val paymentService: PaymentService) {

    @Transactional
    fun createOrder(customerId: Long, totalAmount: BigDecimal): Order {
        val order = Order(
            customerId = customerId,
            totalAmount = totalAmount,
            status = OrderStatus.PENDING
        )

        val savedOrder = orderRepository.save(order)

        // Process payment automatically
        val paymentSuccess = paymentService.processPayment(savedOrder.id!!, totalAmount, "CREDIT_CARD")

        if (paymentSuccess) {
            savedOrder.status = OrderStatus.PAID
            orderRepository.save(savedOrder)
        }

        return savedOrder
    }

    @Transactional
    fun completeOrder(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        if (order.status != OrderStatus.PAID) {
            throw IllegalStateException("Order must be paid before completion")
        }

        order.status = OrderStatus.COMPLETED
        orderRepository.save(order)
    }

    @Transactional
    fun cancelOrder(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        order.status = OrderStatus.CANCELLED
        orderRepository.save(order)

        // Refund payment if order was paid
        if (order.status == OrderStatus.PAID) {
            paymentService.refundPayment(orderId)
        }
    }

    private lateinit var orderRepository: OrderRepository
}

@Service
class PaymentService
constructor(private val orderService: OrderService) {

    @Transactional
    fun processPayment(orderId: Long, amount: BigDecimal, paymentMethod: String): Boolean {
        val payment = Payment(
            orderId = orderId,
            amount = amount,
            paymentMethod = paymentMethod,
            status = PaymentStatus.PENDING
        )

        try {
            // Simulate payment gateway call
            val paymentSuccessful = executePaymentGateway(amount, paymentMethod)

            if (paymentSuccessful) {
                payment.status = PaymentStatus.COMPLETED
                paymentRepository.save(payment)

                // Update order status through OrderService
                orderService.completeOrder(orderId)

                return true
            } else {
                payment.status = PaymentStatus.FAILED
                paymentRepository.save(payment)
                return false
            }
        } catch (e: Exception) {
            payment.status = PaymentStatus.FAILED
            paymentRepository.save(payment)
            throw e
        }
    }

    @Transactional
    fun refundPayment(orderId: Long) {
        val payments = paymentRepository.findAll()
            .filter { it.orderId == orderId && it.status == PaymentStatus.COMPLETED }

        payments.forEach { payment ->
            // Process refund through payment gateway
            executeRefundGateway(payment.amount, payment.paymentMethod)
            payment.status = PaymentStatus.FAILED // Reusing FAILED for refunded
            paymentRepository.save(payment)
        }
    }

    private fun executePaymentGateway(amount: BigDecimal, paymentMethod: String): Boolean {
        // Simulate payment processing
        return amount > BigDecimal.ZERO
    }

    private fun executeRefundGateway(amount: BigDecimal, paymentMethod: String) {
        // Simulate refund processing
    }

    private lateinit var paymentRepository: PaymentRepository
}
