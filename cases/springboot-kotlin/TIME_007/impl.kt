package com.example.shipping.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.DayOfWeek
import java.time.LocalDate
import java.time.LocalDateTime

@Service
@Transactional
class ShippingCalculationService(
    private val shipmentRepository: ShipmentRepository,
    private val shippingMethodRepository: ShippingMethodRepository,
    private val trackingService: TrackingService
) {

    fun calculateDeliveryDate(shipDate: LocalDate, businessDays: Int): LocalDate {
        var currentDate = shipDate
        var remainingDays = businessDays

        while (remainingDays > 0) {
            currentDate = currentDate.plusDays(1)
            remainingDays--
        }

        return currentDate
    }

    @Transactional
    fun createShipment(orderId: Long, shippingMethodCode: String): Shipment {
        val shippingMethod = shippingMethodRepository.findByCode(shippingMethodCode)
            ?: throw IllegalArgumentException("Invalid shipping method: $shippingMethodCode")

        if (!shippingMethod.active) {
            throw IllegalStateException("Shipping method $shippingMethodCode is not active")
        }

        val shipDate = LocalDate.now()
        val estimatedDeliveryDate = calculateDeliveryDate(shipDate, shippingMethod.businessDays)

        val trackingNumber = trackingService.generateTrackingNumber()

        val shipment = Shipment(
            orderId = orderId,
            shippingMethod = shippingMethod.name,
            shipDate = shipDate,
            estimatedDeliveryDate = estimatedDeliveryDate,
            actualDeliveryDate = null,
            status = ShipmentStatus.PENDING,
            trackingNumber = trackingNumber,
            createdAt = LocalDateTime.now()
        )

        return shipmentRepository.save(shipment)
    }

    fun getShippingEstimate(shippingMethodCode: String, orderDate: LocalDate): ShippingEstimate {
        val shippingMethod = shippingMethodRepository.findByCode(shippingMethodCode)
            ?: throw IllegalArgumentException("Invalid shipping method: $shippingMethodCode")

        val estimatedDeliveryDate = calculateDeliveryDate(orderDate, shippingMethod.businessDays)

        return ShippingEstimate(
            methodName = shippingMethod.name,
            methodCode = shippingMethod.code,
            businessDays = shippingMethod.businessDays,
            estimatedDeliveryDate = estimatedDeliveryDate,
            price = shippingMethod.price
        )
    }

    fun getAllShippingEstimates(orderDate: LocalDate): List<ShippingEstimate> {
        val activeMethods = shippingMethodRepository.findByActiveTrue()

        return activeMethods.map { method ->
            ShippingEstimate(
                methodName = method.name,
                methodCode = method.code,
                businessDays = method.businessDays,
                estimatedDeliveryDate = calculateDeliveryDate(orderDate, method.businessDays),
                price = method.price
            )
        }.sortedBy { it.businessDays }
    }

    @Transactional
    fun updateShipmentStatus(shipmentId: Long, newStatus: ShipmentStatus): Shipment {
        val shipment = shipmentRepository.findById(shipmentId)
            .orElseThrow { IllegalArgumentException("Shipment not found: $shipmentId") }

        val updatedShipment = when (newStatus) {
            ShipmentStatus.DELIVERED -> shipment.copy(
                status = newStatus,
                actualDeliveryDate = LocalDate.now()
            )
            else -> shipment.copy(status = newStatus)
        }

        return shipmentRepository.save(updatedShipment)
    }

    fun getDeliveryPerformanceMetrics(startDate: LocalDate, endDate: LocalDate): DeliveryMetrics {
        val shipments = shipmentRepository.findByStatus(ShipmentStatus.DELIVERED)
            .filter { it.actualDeliveryDate != null }
            .filter { !it.actualDeliveryDate!!.isBefore(startDate) && !it.actualDeliveryDate!!.isAfter(endDate) }

        val onTimeDeliveries = shipments.count { shipment ->
            shipment.actualDeliveryDate!! <= shipment.estimatedDeliveryDate
        }

        val lateDeliveries = shipments.count { shipment ->
            shipment.actualDeliveryDate!! > shipment.estimatedDeliveryDate
        }

        val totalDeliveries = shipments.size
        val onTimePercentage = if (totalDeliveries > 0) {
            (onTimeDeliveries.toDouble() / totalDeliveries * 100)
        } else {
            0.0
        }

        return DeliveryMetrics(
            totalDeliveries = totalDeliveries,
            onTimeDeliveries = onTimeDeliveries,
            lateDeliveries = lateDeliveries,
            onTimePercentage = onTimePercentage
        )
    }

    fun getUpcomingDeliveries(targetDate: LocalDate): List<ShipmentSummary> {
        return shipmentRepository.findByEstimatedDeliveryDate(targetDate)
            .filter { it.status != ShipmentStatus.DELIVERED && it.status != ShipmentStatus.FAILED }
            .map { shipment ->
                ShipmentSummary(
                    shipmentId = shipment.id,
                    orderId = shipment.orderId,
                    trackingNumber = shipment.trackingNumber,
                    shippingMethod = shipment.shippingMethod,
                    shipDate = shipment.shipDate,
                    estimatedDeliveryDate = shipment.estimatedDeliveryDate,
                    status = shipment.status
                )
            }
            .sortedBy { it.orderId }
    }
}

data class ShippingEstimate(
    val methodName: String,
    val methodCode: String,
    val businessDays: Int,
    val estimatedDeliveryDate: LocalDate,
    val price: BigDecimal
)

data class DeliveryMetrics(
    val totalDeliveries: Int,
    val onTimeDeliveries: Int,
    val lateDeliveries: Int,
    val onTimePercentage: Double
)

data class ShipmentSummary(
    val shipmentId: Long,
    val orderId: Long,
    val trackingNumber: String?,
    val shippingMethod: String,
    val shipDate: LocalDate,
    val estimatedDeliveryDate: LocalDate,
    val status: ShipmentStatus
)

interface TrackingService {
    fun generateTrackingNumber(): String
}
