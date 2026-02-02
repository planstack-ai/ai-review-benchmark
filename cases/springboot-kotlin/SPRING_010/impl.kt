package com.example.order.listener

import com.example.order.event.OrderCreatedEvent
import com.example.order.entity.Inventory
import com.example.order.entity.Notification
import com.example.order.entity.OrderAnalytics
import com.example.order.repository.InventoryRepository
import com.example.order.repository.NotificationRepository
import com.example.order.repository.OrderAnalyticsRepository
import org.springframework.context.event.EventListener
import org.springframework.stereotype.Component
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Component
class OrderEventListeners(
    private val inventoryRepository: InventoryRepository,
    private val notificationRepository: NotificationRepository,
    private val orderAnalyticsRepository: OrderAnalyticsRepository
) {

    // This listener should run first to reserve inventory
    @EventListener
    @Transactional
    fun handleInventoryReservation(event: OrderCreatedEvent) {
        event.productIds.forEach { productId ->
            val inventory = inventoryRepository.findByProductId(productId)
                ?: throw IllegalStateException("Product not found: $productId")

            if (inventory.quantity - inventory.reservedQuantity < 1) {
                throw IllegalStateException("Insufficient inventory for product: $productId")
            }

            inventory.reservedQuantity += 1
            inventoryRepository.save(inventory)
        }
    }

    // This listener should run second, after inventory is reserved
    @EventListener
    @Transactional
    fun handleCustomerNotification(event: OrderCreatedEvent) {
        val notification = Notification(
            orderId = event.orderId,
            customerId = event.customerId,
            message = "Your order #${event.orderId} has been created successfully. Total: ${event.totalAmount}",
            sentAt = LocalDateTime.now()
        )

        notificationRepository.save(notification)
    }

    // This listener should run third, after notification is sent
    @EventListener
    @Transactional
    fun handleOrderAnalytics(event: OrderCreatedEvent) {
        val analytics = OrderAnalytics(
            orderId = event.orderId,
            eventType = "ORDER_CREATED",
            recordedAt = LocalDateTime.now()
        )

        orderAnalyticsRepository.save(analytics)
    }

    // This listener depends on all previous listeners completing
    @EventListener
    @Transactional
    fun handleOrderConfirmation(event: OrderCreatedEvent) {
        // Verify inventory was reserved
        val inventoryReserved = event.productIds.all { productId ->
            val inventory = inventoryRepository.findByProductId(productId)
            inventory?.reservedQuantity ?: 0 > 0
        }

        if (!inventoryReserved) {
            throw IllegalStateException("Cannot confirm order - inventory not reserved")
        }

        // Send confirmation notification
        val confirmationNotification = Notification(
            orderId = event.orderId,
            customerId = event.customerId,
            message = "Your order #${event.orderId} has been confirmed and is being processed.",
            sentAt = LocalDateTime.now()
        )

        notificationRepository.save(confirmationNotification)
    }
}

data class Notification(
    val id: Long? = null,
    val orderId: Long,
    val customerId: Long,
    val message: String,
    val sentAt: LocalDateTime
)

data class OrderAnalytics(
    val id: Long? = null,
    val orderId: Long,
    val eventType: String,
    val recordedAt: LocalDateTime
)
