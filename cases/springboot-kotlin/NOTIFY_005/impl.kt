package com.example.ecommerce.service

import com.example.ecommerce.model.*
import com.example.ecommerce.repository.*
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Service
@Transactional
class RefundProcessingService(
    private val orderRepository: OrderRepository,
    private val refundRepository: RefundRepository,
    private val userRepository: UserRepository,
    private val refundNotificationRepository: RefundNotificationRepository,
    private val emailService: EmailService
) {

    private val logger = LoggerFactory.getLogger(RefundProcessingService::class.java)

    fun processRefund(orderId: Long, refundAmount: BigDecimal, reason: String, processedByUserId: Long): RefundResult {
        logger.info("Processing refund for order ID: $orderId by user $processedByUserId")

        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val user = userRepository.findById(processedByUserId)
            .orElseThrow { IllegalArgumentException("User not found: $processedByUserId") }

        require(user.role == UserRole.ADMIN || user.role == UserRole.SUPPORT) {
            "Only admin or support users can process refunds"
        }

        validateRefundAmount(order, refundAmount)

        val refund = Refund(
            order = order,
            refundAmount = refundAmount,
            refundMethod = "ORIGINAL_PAYMENT_METHOD",
            reason = reason,
            processedByUserId = processedByUserId,
            status = RefundStatus.PROCESSING
        )

        refundRepository.save(refund)

        try {
            processRefundWithPaymentGateway(refund)

            refund.status = RefundStatus.COMPLETED
            refund.processedAt = LocalDateTime.now()
            refundRepository.save(refund)

            order.status = OrderStatus.REFUNDED
            orderRepository.save(order)

            logger.info("Refund completed for order ${order.orderNumber}, amount: $refundAmount")

            sendRefundNotification(refund, order, user)

            return RefundResult(
                success = true,
                refundId = refund.id,
                message = "Refund processed successfully"
            )

        } catch (e: Exception) {
            logger.error("Refund processing failed for order ${order.orderNumber}: ${e.message}", e)

            refund.status = RefundStatus.REJECTED
            refundRepository.save(refund)

            return RefundResult(
                success = false,
                refundId = refund.id,
                message = "Refund failed: ${e.message}"
            )
        }
    }

    private fun sendRefundNotification(refund: Refund, order: Order, user: User) {
        logger.info("Sending refund notification for order ${order.orderNumber}")

        val emailContent = buildRefundEmailContent(refund, order)
        val subject = "Refund Confirmation for Order #${order.orderNumber}"

        try {
            emailService.sendEmail(
                to = user.email,
                subject = subject,
                body = emailContent
            )

            val notification = RefundNotification(
                refundId = refund.id,
                recipientEmail = user.email,
                sentAt = LocalDateTime.now(),
                status = NotificationStatus.SENT
            )
            refundNotificationRepository.save(notification)

            logger.info("Refund notification sent successfully to ${user.email}")

        } catch (e: Exception) {
            logger.error("Failed to send refund notification: ${e.message}", e)

            val notification = RefundNotification(
                refundId = refund.id,
                recipientEmail = user.email,
                sentAt = LocalDateTime.now(),
                status = NotificationStatus.FAILED
            )
            refundNotificationRepository.save(notification)
        }
    }

    private fun buildRefundEmailContent(refund: Refund, order: Order): String {
        val dateFormatter = DateTimeFormatter.ofPattern("MMMM dd, yyyy")
        val processedDate = refund.processedAt?.format(dateFormatter) ?: "Today"

        return buildString {
            appendLine("Dear Valued Customer,")
            appendLine()
            appendLine("Your refund has been processed successfully.")
            appendLine()
            appendLine("Refund Details:")
            appendLine("Order Number: ${order.orderNumber}")
            appendLine("Refund Amount: $${String.format("%.2f", refund.refundAmount)}")
            appendLine("Refund Method: ${refund.refundMethod}")
            appendLine("Processed Date: $processedDate")
            appendLine()
            if (refund.reason != null) {
                appendLine("Reason: ${refund.reason}")
                appendLine()
            }
            appendLine("The refund will appear in your account within 5-10 business days,")
            appendLine("depending on your financial institution.")
            appendLine()
            appendLine("If you have any questions about this refund, please contact our support team.")
            appendLine()
            appendLine("Thank you for your understanding.")
            appendLine()
            appendLine("Best regards,")
            appendLine("Customer Support Team")
        }
    }

    private fun validateRefundAmount(order: Order, refundAmount: BigDecimal) {
        require(refundAmount > BigDecimal.ZERO) {
            "Refund amount must be positive"
        }

        require(refundAmount <= order.totalAmount) {
            "Refund amount cannot exceed order total"
        }

        val previousRefunds = refundRepository.findByOrderId(order.id)
            .filter { it.status == RefundStatus.COMPLETED }
            .sumOf { it.refundAmount }

        val remainingAmount = order.totalAmount.subtract(previousRefunds)

        require(refundAmount <= remainingAmount) {
            "Refund amount exceeds remaining refundable amount"
        }
    }

    private fun processRefundWithPaymentGateway(refund: Refund) {
        Thread.sleep(100)
        logger.debug("Payment gateway refund completed for refund ID ${refund.id}")
    }
}

data class RefundResult(
    val success: Boolean,
    val refundId: Long,
    val message: String
)
