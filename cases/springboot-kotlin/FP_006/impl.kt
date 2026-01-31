package com.example.payment

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.transaction.annotation.Propagation
import java.math.BigDecimal

/**
 * Payment processing service with proper nested transaction handling.
 *
 * This service uses nested transactions with REQUIRES_NEW propagation to ensure
 * audit logs and notifications are persisted independently of the main business
 * transaction. This is a correct pattern for separating concerns and ensuring
 * compliance requirements are met.
 */
@Service
class PaymentService(
    private val orderRepository: OrderRepository,
    private val auditLogRepository: AuditLogRepository,
    private val notificationQueueRepository: NotificationQueueRepository
) {

    /**
     * Process a payment order with independent audit and notification tracking.
     *
     * The outer transaction handles the order processing. Even if this transaction
     * fails and rolls back, the audit log and notification will be persisted due
     * to their independent transaction boundaries.
     *
     * @param customerId Customer ID
     * @param amount Payment amount
     * @return Created order
     * @throws PaymentException if payment validation fails
     */
    @Transactional
    fun processPayment(customerId: Long, amount: BigDecimal): Order {
        // Log payment attempt in independent transaction (always persists)
        logAudit("Order", 0, "PAYMENT_ATTEMPT", "Customer: $customerId, Amount: $amount")

        // Validate payment (may throw exception and rollback order transaction)
        if (amount <= BigDecimal.ZERO) {
            // Queue failure notification in independent transaction (always persists)
            queueNotification("customer-$customerId", "Payment validation failed: invalid amount")
            throw PaymentException("Payment amount must be positive")
        }

        // Create order
        val order = Order(
            customerId = customerId,
            amount = amount,
            status = "COMPLETED"
        )
        val savedOrder = orderRepository.save(order)

        // Log successful payment in independent transaction
        logAudit("Order", savedOrder.id ?: 0, "PAYMENT_SUCCESS", "Amount: $amount")

        // Queue success notification in independent transaction
        queueNotification("customer-$customerId", "Payment processed successfully: ${savedOrder.id}")

        return savedOrder
    }

    /**
     * Log audit entry in independent transaction.
     *
     * REQUIRES_NEW propagation ensures this operation commits in its own transaction,
     * independent of the caller's transaction. This guarantees audit logs are preserved
     * for compliance even if the main operation fails.
     *
     * This is the CORRECT approach for audit logging in enterprise applications.
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun logAudit(entityType: String, entityId: Long, action: String, details: String) {
        val auditLog = AuditLog(
            entityType = entityType,
            entityId = entityId,
            action = action,
            details = details
        )
        auditLogRepository.save(auditLog)
    }

    /**
     * Queue notification in independent transaction.
     *
     * REQUIRES_NEW propagation ensures notifications are queued regardless of
     * the main transaction outcome. This guarantees customers receive communication
     * about both successful and failed operations.
     *
     * This is the CORRECT approach for notification systems that require guaranteed delivery.
     */
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun queueNotification(recipient: String, message: String) {
        val notification = NotificationQueue(
            recipient = recipient,
            message = message,
            status = "PENDING"
        )
        notificationQueueRepository.save(notification)
    }
}

class PaymentException(message: String) : RuntimeException(message)
