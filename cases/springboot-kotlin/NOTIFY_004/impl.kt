package com.example.ecommerce.service

import com.example.ecommerce.model.*
import com.example.ecommerce.repository.CustomerRepository
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.ShipmentRepository
import org.slf4j.LoggerFactory
import org.springframework.mail.SimpleMailMessage
import org.springframework.mail.javamail.JavaMailSender
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

@Service
@Transactional
class ShippingNotificationService(
    private val orderRepository: OrderRepository,
    private val customerRepository: CustomerRepository,
    private val shipmentRepository: ShipmentRepository,
    private val mailSender: JavaMailSender,
    private val emailTemplateService: EmailTemplateService
) {

    private val logger = LoggerFactory.getLogger(ShippingNotificationService::class.java)

    fun processShipment(orderId: Long, trackingNumber: String, carrier: String) {
        logger.info("Processing shipment for order ID: $orderId")

        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        require(order.status == OrderStatus.CONFIRMED || order.status == OrderStatus.PROCESSING) {
            "Order must be in CONFIRMED or PROCESSING status to ship"
        }

        val shipment = Shipment(
            order = order,
            trackingNumber = trackingNumber,
            carrier = carrier,
            shippedAt = LocalDateTime.now()
        )

        shipmentRepository.save(shipment)

        order.status = OrderStatus.SHIPPED
        orderRepository.save(order)

        logger.info("Order $orderId marked as shipped, sending notification")

        sendShippingNotificationEmail(order, shipment)
    }

    private fun sendShippingNotificationEmail(order: Order, shipment: Shipment) {
        logger.debug("Preparing shipping notification email for order ${order.orderNumber}")

        val customer = customerRepository.findById(order.customerId)
            .orElseThrow { IllegalStateException("Customer not found for order ${order.id}") }

        val shippingAddress = order.shippingAddress
            ?: throw IllegalStateException("Shipping address not found for order ${order.id}")

        val emailContent = buildShippingEmailContent(
            customer = customer,
            order = order,
            shipment = shipment,
            shippingAddress = shippingAddress
        )

        val message = SimpleMailMessage().apply {
            setTo(customer.email)
            setSubject("Your Order #${order.orderNumber} Has Shipped!")
            setText(emailContent)
        }

        try {
            mailSender.send(message)
            logger.info("Shipping notification sent to ${customer.email} for order ${order.orderNumber}")
        } catch (e: Exception) {
            logger.error("Failed to send shipping notification for order ${order.orderNumber}: ${e.message}", e)
            throw e
        }
    }

    private fun buildShippingEmailContent(
        customer: Customer,
        order: Order,
        shipment: Shipment,
        shippingAddress: ShippingAddress
    ): String {
        val dateFormatter = DateTimeFormatter.ofPattern("MMMM dd, yyyy")
        val shippedDate = shipment.shippedAt.format(dateFormatter)

        return buildString {
            appendLine("Dear ${customer.fullName},")
            appendLine()
            appendLine("Great news! Your order has been shipped and is on its way to you.")
            appendLine()
            appendLine("Order Information:")
            appendLine("Order Number: ${order.orderNumber}")
            appendLine("Shipped Date: $shippedDate")
            appendLine()
            appendLine("Shipping Details:")
            appendLine("Carrier: ${shipment.carrier}")
            appendLine("Tracking Number: ${shipment.trackingNumber}")
            appendLine()
            if (shipment.estimatedDelivery != null) {
                appendLine("Estimated Delivery: ${shipment.estimatedDelivery.format(dateFormatter)}")
                appendLine()
            }
            appendLine("Shipping Address:")
            if (shippingAddress.recipientName != null) {
                appendLine(shippingAddress.recipientName)
            }
            appendLine(shippingAddress.streetAddress)
            appendLine("${shippingAddress.city}, ${shippingAddress.state} ${shippingAddress.postalCode}")
            appendLine(shippingAddress.country)
            appendLine()
            appendLine("You can track your shipment using the tracking number provided above.")
            appendLine()
            appendLine("Thank you for your order!")
            appendLine()
            appendLine("Best regards,")
            appendLine("The E-Commerce Team")
        }
    }

    fun getShipmentStatus(orderId: Long): ShipmentStatusResponse {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val shipment = shipmentRepository.findByOrderId(orderId)

        return ShipmentStatusResponse(
            orderId = order.id,
            orderNumber = order.orderNumber,
            orderStatus = order.status,
            trackingNumber = shipment?.trackingNumber,
            carrier = shipment?.carrier,
            shippedAt = shipment?.shippedAt,
            estimatedDelivery = shipment?.estimatedDelivery
        )
    }
}

data class ShipmentStatusResponse(
    val orderId: Long,
    val orderNumber: String,
    val orderStatus: OrderStatus,
    val trackingNumber: String?,
    val carrier: String?,
    val shippedAt: LocalDateTime?,
    val estimatedDelivery: LocalDate?
)
