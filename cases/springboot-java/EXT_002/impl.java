package com.example.ecommerce.controller;

import com.example.ecommerce.dto.WebhookPayload;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.service.NotificationService;
import com.example.ecommerce.service.InventoryService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/webhooks")
public class PaymentWebhookController {

    private static final Logger logger = LoggerFactory.getLogger(PaymentWebhookController.class);

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private NotificationService notificationService;

    @Autowired
    private InventoryService inventoryService;

    @PostMapping("/payment")
    public ResponseEntity<String> handlePaymentWebhook(@RequestBody WebhookPayload payload) {
        logger.info("Received payment webhook: eventId={}, type={}",
                payload.getEventId(), payload.getEventType());

        try {
            switch (payload.getEventType()) {
                case "payment.completed":
                    handlePaymentCompleted(payload);
                    break;
                case "payment.failed":
                    handlePaymentFailed(payload);
                    break;
                case "payment.refunded":
                    handlePaymentRefunded(payload);
                    break;
                default:
                    logger.warn("Unknown webhook event type: {}", payload.getEventType());
            }

            return ResponseEntity.ok("Webhook processed");

        } catch (Exception e) {
            logger.error("Error processing webhook: {}", payload.getEventId(), e);
            return ResponseEntity.internalServerError().body("Processing failed");
        }
    }

    private void handlePaymentCompleted(WebhookPayload payload) {
        Long orderId = payload.getData().getOrderId();
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        order.setStatus("PAID");
        order.setPaymentTransactionId(payload.getData().getPaymentId());
        orderRepository.save(order);

        inventoryService.confirmReservation(orderId);

        notificationService.sendOrderConfirmation(order.getUserId(), orderId);

        logger.info("Payment completed for order: {}", orderId);
    }

    private void handlePaymentFailed(WebhookPayload payload) {
        Long orderId = payload.getData().getOrderId();
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        order.setStatus("PAYMENT_FAILED");
        order.setFailureReason(payload.getData().getFailureReason());
        orderRepository.save(order);

        inventoryService.releaseReservation(orderId);

        notificationService.sendPaymentFailedNotification(order.getUserId(), orderId);

        logger.info("Payment failed for order: {}", orderId);
    }

    private void handlePaymentRefunded(WebhookPayload payload) {
        Long orderId = payload.getData().getOrderId();
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        order.setStatus("REFUNDED");
        order.setRefundedAt(payload.getCreatedAt());
        orderRepository.save(order);

        inventoryService.restoreStock(orderId);

        notificationService.sendRefundConfirmation(order.getUserId(), orderId);

        logger.info("Payment refunded for order: {}", orderId);
    }
}
