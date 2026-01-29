package com.example.ecommerce.controller

import com.example.ecommerce.dto.WebhookPayload
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.service.InventoryService
import com.example.ecommerce.service.NotificationService
import org.slf4j.LoggerFactory
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/webhooks")
class PaymentWebhookController(
    private val orderRepository: OrderRepository,
    private val notificationService: NotificationService,
    private val inventoryService: InventoryService
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @PostMapping("/payment")
    fun handlePaymentWebhook(@RequestBody payload: WebhookPayload): ResponseEntity<String> {
        logger.info("Received payment webhook: eventId=${payload.eventId}, type=${payload.eventType}")

        try {
            when (payload.eventType) {
                "payment.completed" -> handlePaymentCompleted(payload)
                "payment.failed" -> handlePaymentFailed(payload)
                "payment.refunded" -> handlePaymentRefunded(payload)
                else -> logger.warn("Unknown webhook event type: ${payload.eventType}")
            }

            return ResponseEntity.ok("Webhook processed")

        } catch (e: Exception) {
            logger.error("Error processing webhook: ${payload.eventId}", e)
            return ResponseEntity.internalServerError().body("Processing failed")
        }
    }

    private fun handlePaymentCompleted(payload: WebhookPayload) {
        val orderId = payload.data.orderId
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        order.status = "PAID"
        order.paymentTransactionId = payload.data.paymentId
        orderRepository.save(order)

        inventoryService.confirmReservation(orderId)
        notificationService.sendOrderConfirmation(order.userId, orderId)

        logger.info("Payment completed for order: $orderId")
    }

    private fun handlePaymentFailed(payload: WebhookPayload) {
        val orderId = payload.data.orderId
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        order.status = "PAYMENT_FAILED"
        order.failureReason = payload.data.failureReason
        orderRepository.save(order)

        inventoryService.releaseReservation(orderId)
        notificationService.sendPaymentFailedNotification(order.userId, orderId)

        logger.info("Payment failed for order: $orderId")
    }

    private fun handlePaymentRefunded(payload: WebhookPayload) {
        val orderId = payload.data.orderId
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        order.status = "REFUNDED"
        order.refundedAt = payload.createdAt
        orderRepository.save(order)

        inventoryService.restoreStock(orderId)
        notificationService.sendRefundConfirmation(order.userId, orderId)

        logger.info("Payment refunded for order: $orderId")
    }
}
