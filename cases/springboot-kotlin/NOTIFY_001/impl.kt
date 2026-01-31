package com.example.ecommerce.service

import com.example.ecommerce.model.Order
import com.example.ecommerce.model.OrderItem
import com.example.ecommerce.repository.OrderRepository
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.mail.SimpleMailMessage
import org.springframework.mail.javamail.JavaMailSender
import org.springframework.scheduling.annotation.Async
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Service
@Transactional
class OrderNotificationService(
    private val orderRepository: OrderRepository,
    private val mailSender: JavaMailSender,
    @Value("\${app.notification.from-email}") private val fromEmail: String,
    @Value("\${app.notification.support-email}") private val supportEmail: String
) {

    private val logger = LoggerFactory.getLogger(OrderNotificationService::class.java)

    fun processOrderConfirmation(orderId: Long) {
        logger.info("Processing order confirmation for order ID: $orderId")
        
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found with ID: $orderId") }
        
        validateOrderForNotification(order)
        sendOrderConfirmationEmail(order)
        updateOrderNotificationStatus(order)
        
        logger.info("Order confirmation processing completed for order ID: $orderId")
    }

    @Async
    fun sendOrderConfirmationEmail(order: Order) {
        logger.debug("Sending confirmation email for order ${order.id} to ${order.customerEmail}")
        
        val emailContent = buildEmailContent(order)
        val subject = "Order Confirmation #${order.orderNumber}"
        
        val message = SimpleMailMessage().apply {
            setFrom(fromEmail)
            setTo(order.customerEmail)
            setSubject(subject)
            setText(emailContent)
        }
        
        mailSender.send(message)
        logger.info("Confirmation email sent successfully for order ${order.id}")
    }

    private fun validateOrderForNotification(order: Order) {
        require(order.customerEmail.isNotBlank()) { 
            "Customer email is required for order ${order.id}" 
        }
        require(order.status == "CONFIRMED") { 
            "Order ${order.id} must be in CONFIRMED status to send notification" 
        }
    }

    private fun buildEmailContent(order: Order): String {
        val formatter = DateTimeFormatter.ofPattern("MMM dd, yyyy 'at' HH:mm")
        val orderDate = order.createdAt.format(formatter)
        
        return buildString {
            appendLine("Dear ${order.customerName},")
            appendLine()
            appendLine("Thank you for your order! We're excited to confirm that we've received your order and it's being processed.")
            appendLine()
            appendLine("Order Details:")
            appendLine("Order Number: ${order.orderNumber}")
            appendLine("Order Date: $orderDate")
            appendLine("Total Amount: ${formatCurrency(order.totalAmount)}")
            appendLine()
            appendLine("Items Ordered:")
            order.items.forEach { item ->
                appendLine("- ${item.productName} (Qty: ${item.quantity}) - ${formatCurrency(item.unitPrice)}")
            }
            appendLine()
            appendLine("Shipping Address:")
            appendLine("${order.shippingAddress.fullName}")
            appendLine("${order.shippingAddress.streetAddress}")
            appendLine("${order.shippingAddress.city}, ${order.shippingAddress.state} ${order.shippingAddress.zipCode}")
            appendLine()
            appendLine("We'll send you another email with tracking information once your order ships.")
            appendLine()
            appendLine("If you have any questions, please contact us at $supportEmail")
            appendLine()
            appendLine("Thank you for your business!")
            appendLine("The E-Commerce Team")
        }
    }

    private fun formatCurrency(amount: BigDecimal): String {
        return "$${String.format("%.2f", amount)}"
    }

    private fun updateOrderNotificationStatus(order: Order) {
        order.emailSentAt = LocalDateTime.now()
        order.notificationStatus = "SENT"
        orderRepository.save(order)
        logger.debug("Updated notification status for order ${order.id}")
    }
}