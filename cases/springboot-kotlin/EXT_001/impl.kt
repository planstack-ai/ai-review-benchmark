package com.example.ecommerce.service

import com.example.ecommerce.client.PaymentGatewayClient
import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.Payment
import com.example.ecommerce.exception.PaymentException
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.PaymentRepository
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.web.client.HttpServerErrorException
import org.springframework.web.client.ResourceAccessException
import java.math.BigDecimal
import java.net.SocketTimeoutException
import java.time.LocalDateTime
import java.util.*

@Service
class PaymentProcessingService(
    private val paymentGatewayClient: PaymentGatewayClient,
    private val orderRepository: OrderRepository,
    private val paymentRepository: PaymentRepository
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Transactional
    fun processPayment(orderId: Long, cardToken: String, amount: BigDecimal): Payment {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val payment = createPendingPayment(order, amount)
        paymentRepository.save(payment)

        try {
            val response = paymentGatewayClient.chargeCard(cardToken, amount)

            if (response.isSuccessful) {
                payment.status = "COMPLETED"
                payment.gatewayTransactionId = response.transactionId
                payment.processedAt = LocalDateTime.now()

                order.status = "PAID"
                order.paymentId = payment.id
                orderRepository.save(order)

                logger.info("Payment successful for order $orderId: ${response.transactionId}")
            } else {
                payment.status = "FAILED"
                payment.failureReason = response.errorMessage

                order.status = "PAYMENT_FAILED"
                orderRepository.save(order)

                logger.warn("Payment failed for order $orderId: ${response.errorMessage}")
            }

        } catch (e: ResourceAccessException) {
            when (e.cause) {
                is SocketTimeoutException -> {
                    logger.error("Payment timeout for order $orderId")
                    payment.status = "FAILED"
                    payment.failureReason = "Payment gateway timeout"
                    order.status = "PAYMENT_FAILED"
                    orderRepository.save(order)
                    throw PaymentException("Payment processing timeout - please try again", e)
                }
                else -> throw PaymentException("Payment processing error", e)
            }
        } catch (e: HttpServerErrorException) {
            logger.error("Payment gateway error for order $orderId: ${e.message}")
            payment.status = "FAILED"
            payment.failureReason = "Payment gateway error: ${e.statusCode}"
            order.status = "PAYMENT_FAILED"
            orderRepository.save(order)
            throw PaymentException("Payment gateway unavailable", e)
        }

        return paymentRepository.save(payment)
    }

    @Transactional
    fun retryPayment(orderId: Long, cardToken: String): Payment {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        if (order.status != "PAYMENT_FAILED") {
            throw IllegalStateException("Order is not in PAYMENT_FAILED state")
        }

        return processPayment(orderId, cardToken, order.totalAmount)
    }

    private fun createPendingPayment(order: Order, amount: BigDecimal): Payment {
        return Payment(
            id = UUID.randomUUID().toString(),
            orderId = order.id!!,
            amount = amount,
            status = "PENDING",
            createdAt = LocalDateTime.now()
        )
    }
}
