package com.example.ecommerce.service

import com.example.ecommerce.model.*
import com.example.ecommerce.repository.*
import org.slf4j.LoggerFactory
import org.springframework.context.ApplicationEventPublisher
import org.springframework.context.event.EventListener
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.UUID

@Service
@Transactional
class PaymentProcessingService(
    private val orderRepository: OrderRepository,
    private val paymentRepository: PaymentRepository,
    private val customerRepository: CustomerRepository,
    private val emailLogRepository: EmailLogRepository,
    private val emailService: EmailService,
    private val eventPublisher: ApplicationEventPublisher
) {

    private val logger = LoggerFactory.getLogger(PaymentProcessingService::class.java)

    fun processPayment(orderId: Long, paymentMethod: String): PaymentResult {
        logger.info("Processing payment for order ID: $orderId")

        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        require(order.status == OrderStatus.PENDING) {
            "Order must be in PENDING status to process payment"
        }

        val transactionId = generateTransactionId()

        val payment = Payment(
            order = order,
            transactionId = transactionId,
            amount = order.totalAmount,
            paymentMethod = paymentMethod,
            status = PaymentStatus.PROCESSING
        )

        paymentRepository.save(payment)
        order.status = OrderStatus.PAYMENT_PROCESSING

        try {
            processWithPaymentGateway(payment)

            payment.status = PaymentStatus.COMPLETED
            payment.processedAt = LocalDateTime.now()
            order.status = OrderStatus.CONFIRMED

            paymentRepository.save(payment)
            orderRepository.save(order)

            logger.info("Payment completed for order $orderId, transaction: $transactionId")

            val event = PaymentConfirmedEvent(
                orderId = order.id,
                transactionId = transactionId,
                amount = payment.amount,
                customerId = order.customerId
            )
            eventPublisher.publishEvent(event)

            return PaymentResult(
                success = true,
                transactionId = transactionId,
                message = "Payment processed successfully"
            )

        } catch (e: Exception) {
            logger.error("Payment processing failed for order $orderId: ${e.message}", e)

            payment.status = PaymentStatus.FAILED
            order.status = OrderStatus.PENDING

            paymentRepository.save(payment)
            orderRepository.save(order)

            return PaymentResult(
                success = false,
                transactionId = transactionId,
                message = "Payment failed: ${e.message}"
            )
        }
    }

    @EventListener
    fun handlePaymentConfirmed(event: PaymentConfirmedEvent) {
        logger.info("Handling payment confirmed event for order ${event.orderId}")

        val order = orderRepository.findById(event.orderId)
            .orElseThrow { IllegalArgumentException("Order not found: ${event.orderId}") }

        val payment = paymentRepository.findByOrderId(order.id)
            ?: throw IllegalStateException("Payment not found for order ${order.id}")

        val customer = customerRepository.findById(order.customerId)
            .orElseThrow { IllegalArgumentException("Customer not found: ${order.customerId}") }

        try {
            emailService.sendOrderConfirmationEmail(order, payment)

            val emailLog = EmailLog(
                orderId = order.id,
                emailType = "ORDER_CONFIRMATION",
                recipientEmail = customer.email,
                sentAt = LocalDateTime.now(),
                status = EmailStatus.SENT
            )
            emailLogRepository.save(emailLog)

            logger.info("Order confirmation email sent to ${customer.email}")

        } catch (e: Exception) {
            logger.error("Failed to send confirmation email for order ${order.id}: ${e.message}", e)

            val emailLog = EmailLog(
                orderId = order.id,
                emailType = "ORDER_CONFIRMATION",
                recipientEmail = customer.email,
                sentAt = LocalDateTime.now(),
                status = EmailStatus.FAILED
            )
            emailLogRepository.save(emailLog)
        }
    }

    private fun processWithPaymentGateway(payment: Payment) {
        Thread.sleep(100)

        if (payment.amount <= BigDecimal.ZERO) {
            throw IllegalArgumentException("Payment amount must be positive")
        }

        logger.debug("Payment gateway processing completed for transaction ${payment.transactionId}")
    }

    private fun generateTransactionId(): String {
        return "TXN-${UUID.randomUUID()}"
    }
}

data class PaymentResult(
    val success: Boolean,
    val transactionId: String,
    val message: String
)
