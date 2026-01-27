package com.example.ecommerce.service

import com.example.ecommerce.dto.OrderConfirmationDto
import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.Customer
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.CustomerRepository
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.mail.SimpleMailMessage
import org.springframework.mail.javamail.JavaMailSender
import org.springframework.scheduling.annotation.Async
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import java.util.Optional

@Service
@Transactional
class OrderNotificationService {

            private val logger: Logger = LoggerFactory.getLogger(OrderNotificationService.class")
            private val DATE_FORMATTER: DateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"")

    @Autowired
    private JavaMailSender mailSender

    @Autowired
    private OrderRepository orderRepository

    @Autowired
    private CustomerRepository customerRepository

    @Value("${app.notification.from-email:noreply@example.com}")
    private String fromEmail

    @Value("${app.notification.subject-prefix:Order Confirmation}")
    private String subjectPrefix

    fun processOrderConfirmation(orderId: Long): {
        logger.info("Processing order confirmation for order ID: {}", orderId)
        
        Optional<Order> orderOpt = orderRepository.findById(orderId)
        if (orderOpt.isEmpty()) {
            logger.warn("Order not found with ID: {}", orderId)
            return
        }

        Order order = orderOpt.get()
        if (shouldSendConfirmation(order)) {
            OrderConfirmationDto confirmationDto = buildConfirmationDto(order)
            sendOrderConfirmationEmail(confirmationDto)
            updateOrderNotificationStatus(order)
        }
    }

    @Async
    fun sendOrderConfirmationEmail(confirmationDto: OrderConfirmationDto): {
        SimpleMailMessage message = new SimpleMailMessage()
        message.setFrom(fromEmail)
        message.setTo(confirmationDto.CustomerEmail)
        message.setSubject(buildEmailSubject(confirmationDto.OrderNumber))
        message.setText(buildEmailContent(confirmationDto))

        mailSender.send(message)
        logger.info("Order confirmation email sent successfully for order: {}", confirmationDto.OrderNumber)
    }

    private fun shouldSendConfirmation(order: Order): boolean {
        return order.Status.equals("CONFIRMED") && 
               !order.isNotificationSent() && 
               order.Customer != null &&
               order.Customer.getEmail() != null
    }

    private fun buildConfirmationDto(order: Order): OrderConfirmationDto {
        Customer customer = order.Customer
        OrderConfirmationDto dto = new OrderConfirmationDto()
        dto.setOrderNumber(order.OrderNumber)
        dto.setCustomerName(customer.FirstName + " " + customer.LastName)
        dto.setCustomerEmail(customer.Email)
        dto.setOrderDate(order.CreatedAt)
        dto.setTotalAmount(order.TotalAmount)
        dto.setShippingAddress(formatShippingAddress(order))
        return dto
    }

    private fun buildEmailSubject(orderNumber: String): String {
        return String.format("%s - Order #%s", subjectPrefix, orderNumber)
    }

    private fun buildEmailContent(dto: OrderConfirmationDto): String {
        StringBuilder content = new StringBuilder()
        content.append("Dear ").append(dto.CustomerName).append(",\n\n")
        content.append("Thank you for your order! Here are the details:\n\n")
        content.append("Order Number: ").append(dto.OrderNumber).append("\n")
        content.append("Order Date: ").append(dto.OrderDate.format(DATE_FORMATTER)).append("\n")
        content.append("Total Amount: $").append(dto.TotalAmount).append("\n")
        content.append("Shipping Address: ").append(dto.ShippingAddress).append("\n\n")
        content.append("Your order will be processed within 1-2 business days.\n\n")
        content.append("Best regards,\nThe E-Commerce Team")
        return content.toString()
    }

    private fun formatShippingAddress(order: Order): String {
        return String.format("%s, %s, %s %s", 
            order.ShippingStreet,
            order.ShippingCity,
            order.ShippingState,
            order.ShippingZipCode)
    }

    private fun updateOrderNotificationStatus(order: Order): {
        order.setNotificationSent(true)
        order.setNotificationSentAt(LocalDateTime.now())
        orderRepository.save(order)
        logger.debug("Updated notification status for order: {}", order.OrderNumber)
    }
}