package com.example.ecommerce.service

import com.example.ecommerce.client.FulfillmentApiClient
import com.example.ecommerce.dto.FulfillmentRequest
import com.example.ecommerce.entity.Order
import com.example.ecommerce.repository.OrderRepository
import org.slf4j.LoggerFactory
import org.springframework.retry.annotation.Backoff
import org.springframework.retry.annotation.Retryable
import org.springframework.stereotype.Service
import org.springframework.web.client.RestClientException
import java.time.LocalDateTime

@Service
class FulfillmentService(
    private val fulfillmentApiClient: FulfillmentApiClient,
    private val orderRepository: OrderRepository
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Retryable(
        retryFor = [RestClientException::class],
        maxAttempts = 3,
        backoff = Backoff(delay = 1000, multiplier = 2.0)
    )
    fun submitOrderForFulfillment(orderId: Long): String {
        logger.info("Submitting order $orderId for fulfillment")

        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val request = buildFulfillmentRequest(order)

        val response = fulfillmentApiClient.submitOrder(request)

        order.fulfillmentId = response.fulfillmentId
        order.status = "SUBMITTED_FOR_FULFILLMENT"
        order.submittedAt = LocalDateTime.now()
        orderRepository.save(order)

        logger.info("Order $orderId submitted successfully, fulfillment ID: ${response.fulfillmentId}")

        return response.fulfillmentId
    }

    @Retryable(
        retryFor = [RestClientException::class],
        maxAttempts = 5,
        backoff = Backoff(delay = 500, multiplier = 1.5)
    )
    fun createShipment(order: Order) {
        logger.info("Creating shipment for order ${order.id}")

        val request = FulfillmentRequest(
            orderId = order.id.toString(),
            customerId = order.customerId,
            shippingAddress = order.shippingAddress,
            items = order.items
        )

        val response = fulfillmentApiClient.createShipment(request)

        order.trackingNumber = response.trackingNumber
        order.carrier = response.carrier
        order.status = "SHIPPED"
        orderRepository.save(order)
    }

    @Retryable(
        retryFor = [RestClientException::class],
        maxAttempts = 3,
        backoff = Backoff(delay = 2000)
    )
    fun updateInventoryExternal(productId: String, quantity: Int) {
        logger.info("Updating external inventory for product $productId: $quantity")

        fulfillmentApiClient.updateInventory(productId, quantity)

        logger.info("External inventory updated for product $productId")
    }

    private fun buildFulfillmentRequest(order: Order): FulfillmentRequest {
        return FulfillmentRequest(
            orderId = order.id.toString(),
            customerId = order.customerId,
            shippingAddress = order.shippingAddress,
            items = order.items,
            priority = determinePriority(order)
        )
    }

    private fun determinePriority(order: Order): String {
        return if (order.isExpressShipping) "HIGH" else "NORMAL"
    }
}
