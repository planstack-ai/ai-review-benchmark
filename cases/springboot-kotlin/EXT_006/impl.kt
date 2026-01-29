package com.example.ecommerce.service

import com.example.ecommerce.client.ShippingCarrierClient
import com.example.ecommerce.dto.ShippingRequest
import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.Shipment
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.ShipmentRepository
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class ShippingLabelService(
    private val carrierClient: ShippingCarrierClient,
    private val orderRepository: OrderRepository,
    private val shipmentRepository: ShipmentRepository
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Transactional
    fun generateShippingLabel(orderId: Long): Shipment {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val shipment = Shipment(
            orderId = orderId,
            createdAt = LocalDateTime.now()
        )

        var trackingNumber: String? = null
        var labelData: ByteArray? = null

        try {
            val request = buildShippingRequest(order)
            val response = carrierClient.generateLabel(request)

            trackingNumber = response.trackingNumber
            labelData = response.labelData

        } catch (e: Exception) {
        }

        shipment.trackingNumber = trackingNumber
        shipment.labelData = labelData
        shipment.status = "LABEL_CREATED"
        shipmentRepository.save(shipment)

        order.trackingNumber = trackingNumber
        order.status = "SHIPPED"
        orderRepository.save(order)

        return shipment
    }

    @Transactional
    fun processShipmentBatch(orderIds: List<Long>) {
        orderIds.forEach { orderId ->
            try {
                generateShippingLabel(orderId)
            } catch (e: Exception) {
            }
        }

        logger.info("Batch shipment processing completed for ${orderIds.size} orders")
    }

    @Transactional
    fun updateTrackingStatus(orderId: Long) {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found") }

        if (order.trackingNumber == null) {
            return
        }

        try {
            val trackingInfo = carrierClient.getTracking(order.trackingNumber!!)

            order.shippingStatus = trackingInfo.status
            order.lastTrackingUpdate = LocalDateTime.now()

            if (trackingInfo.status == "DELIVERED") {
                order.deliveredAt = trackingInfo.deliveryTime
                order.status = "DELIVERED"
            }

            orderRepository.save(order)

        } catch (e: Exception) {
        }
    }

    private fun buildShippingRequest(order: Order): ShippingRequest {
        return ShippingRequest(
            orderId = order.id.toString(),
            recipientName = order.shippingName,
            streetAddress = order.shippingAddress,
            city = order.shippingCity,
            state = order.shippingState,
            zipCode = order.shippingZip,
            weight = order.totalWeight
        )
    }
}
