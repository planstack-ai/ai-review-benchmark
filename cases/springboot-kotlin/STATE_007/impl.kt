package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional
class DeliveryStatusService(
    private val deliveryRepository: DeliveryRepository,
    private val statusHistoryRepository: DeliveryStatusHistoryRepository,
    private val notificationService: NotificationService
) {

    fun updateDeliveryStatus(
        orderId: Long,
        newStatus: DeliveryStatus,
        updatedBy: String
    ): DeliveryStatusUpdateResult {
        val delivery = deliveryRepository.findByOrderId(orderId)
            ?: throw IllegalArgumentException("Delivery not found for order: $orderId")

        val oldStatus = delivery.status

        delivery.status = newStatus

        if (newStatus == DeliveryStatus.DELIVERED) {
            delivery.actualDelivery = LocalDateTime.now()
        }

        val history = DeliveryStatusHistory(
            deliveryId = delivery.id,
            oldStatus = oldStatus,
            newStatus = newStatus,
            changedBy = updatedBy
        )

        deliveryRepository.save(delivery)
        statusHistoryRepository.save(history)

        notificationService.sendDeliveryStatusUpdate(orderId, newStatus)

        return DeliveryStatusUpdateResult(
            orderId = orderId,
            oldStatus = oldStatus,
            newStatus = newStatus,
            success = true
        )
    }

    fun getDeliveryStatus(orderId: Long): Delivery {
        return deliveryRepository.findByOrderId(orderId)
            ?: throw IllegalArgumentException("Delivery not found for order: $orderId")
    }

    fun setTrackingNumber(orderId: Long, trackingNumber: String, carrier: String): Delivery {
        val delivery = deliveryRepository.findByOrderId(orderId)
            ?: throw IllegalArgumentException("Delivery not found for order: $orderId")

        delivery.trackingNumber = trackingNumber
        delivery.carrier = carrier

        return deliveryRepository.save(delivery)
    }
}

data class DeliveryStatusUpdateResult(
    val orderId: Long,
    val oldStatus: DeliveryStatus,
    val newStatus: DeliveryStatus,
    val success: Boolean
)

data class Delivery(
    val id: Long = 0,
    val orderId: Long,
    var trackingNumber: String? = null,
    var carrier: String? = null,
    var status: DeliveryStatus,
    var estimatedDelivery: LocalDateTime? = null,
    var actualDelivery: LocalDateTime? = null
)

enum class DeliveryStatus {
    PREPARING,
    SHIPPED,
    IN_TRANSIT,
    OUT_FOR_DELIVERY,
    DELIVERED
}

data class DeliveryStatusHistory(
    val id: Long = 0,
    val deliveryId: Long,
    val oldStatus: DeliveryStatus?,
    val newStatus: DeliveryStatus,
    val changedAt: LocalDateTime = LocalDateTime.now(),
    val changedBy: String?
)

interface DeliveryRepository {
    fun findByOrderId(orderId: Long): Delivery?
    fun save(delivery: Delivery): Delivery
}

interface DeliveryStatusHistoryRepository {
    fun save(history: DeliveryStatusHistory): DeliveryStatusHistory
}

interface NotificationService {
    fun sendDeliveryStatusUpdate(orderId: Long, status: DeliveryStatus)
}

class InvalidStatusTransitionException(message: String) : RuntimeException(message)
