package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
@Transactional
class RefundService(
    private val paymentRepository: PaymentRepository,
    private val refundRepository: RefundRepository,
    private val paymentGateway: PaymentGateway,
    private val notificationService: NotificationService
) {

    fun processRefund(orderId: Long, amount: BigDecimal, reason: String?): RefundResponse {
        val payment = paymentRepository.findByOrderId(orderId)
            ?: throw IllegalArgumentException("Payment not found for order: $orderId")

        validateRefund(payment, amount)

        val gatewayResult = paymentGateway.processRefund(payment.id, amount)

        if (!gatewayResult.success) {
            throw RefundFailedException("Refund failed for order: $orderId")
        }

        val refund = Refund(
            paymentId = payment.id,
            amount = amount,
            reason = reason
        )
        refundRepository.save(refund)

        notificationService.sendRefundNotification(orderId, amount)

        return RefundResponse(
            orderId = orderId,
            refundAmount = amount,
            transactionId = gatewayResult.transactionId,
            success = true
        )
    }

    private fun validateRefund(payment: Payment, amount: BigDecimal) {
        if (payment.status != PaymentStatus.PAID) {
            throw IllegalStateException("Cannot refund unpaid order")
        }

        if (amount > payment.amount) {
            throw IllegalArgumentException("Refund amount exceeds payment amount")
        }
    }

    fun getRefundStatus(orderId: Long): PaymentStatus {
        val payment = paymentRepository.findByOrderId(orderId)
            ?: throw IllegalArgumentException("Payment not found for order: $orderId")
        return payment.status
    }
}

data class RefundResponse(
    val orderId: Long,
    val refundAmount: BigDecimal,
    val transactionId: String?,
    val success: Boolean
)

data class Payment(
    val id: Long = 0,
    val orderId: Long,
    val amount: BigDecimal,
    val paymentMethod: PaymentMethod,
    var status: PaymentStatus,
    val paidAt: LocalDateTime?,
    var refundedAt: LocalDateTime? = null
)

enum class PaymentStatus {
    PENDING, PAID, REFUNDED, PARTIALLY_REFUNDED, FAILED
}

enum class PaymentMethod {
    CREDIT_CARD, DEBIT_CARD, BANK_TRANSFER, CASH_ON_DELIVERY
}

data class Refund(
    val id: Long = 0,
    val paymentId: Long,
    val amount: BigDecimal,
    val reason: String?,
    val processedAt: LocalDateTime = LocalDateTime.now()
)

interface PaymentRepository {
    fun findByOrderId(orderId: Long): Payment?
    fun save(payment: Payment): Payment
}

interface RefundRepository {
    fun save(refund: Refund): Refund
}

interface PaymentGateway {
    fun processRefund(paymentId: Long, amount: BigDecimal): RefundResult
}

data class RefundResult(val success: Boolean, val transactionId: String?)

interface NotificationService {
    fun sendRefundNotification(orderId: Long, amount: BigDecimal)
}

class RefundFailedException(message: String) : RuntimeException(message)
