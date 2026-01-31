package com.example.order.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

@Service
@Transactional
class DeliveryScheduleService(
    private val orderRepository: OrderRepository,
    private val deliveryRouteRepository: DeliveryRouteRepository,
    private val notificationService: NotificationService
) {

    fun getOrdersForDeliveryDate(targetDate: LocalDate): List<OrderDeliveryInfo> {
        val targetDateTime = targetDate.atStartOfDay()
        val orders = orderRepository.findAll()
            .filter { order -> order.deliveryDate == targetDateTime }
            .sortedBy { it.orderNumber }

        return orders.map { order ->
            OrderDeliveryInfo(
                orderId = order.id,
                orderNumber = order.orderNumber,
                customerId = order.customerId,
                deliveryDate = order.deliveryDate,
                totalAmount = order.totalAmount,
                status = order.status
            )
        }
    }

    @Transactional
    fun assignOrdersToRoute(routeId: Long, targetDate: LocalDate): RouteAssignmentResult {
        val route = deliveryRouteRepository.findById(routeId)
            .orElseThrow { IllegalArgumentException("Route not found") }

        if (route.deliveryDate != targetDate) {
            return RouteAssignmentResult.INVALID_DATE
        }

        val orders = getOrdersForDeliveryDate(targetDate)

        if (orders.size > DeliveryConstants.MAX_ORDERS_PER_ROUTE) {
            return RouteAssignmentResult.CAPACITY_EXCEEDED
        }

        orders.forEach { orderInfo ->
            val order = orderRepository.findById(orderInfo.orderId).orElseThrow()
            if (order.status == OrderStatus.CONFIRMED) {
                orderRepository.save(order.copy(status = OrderStatus.PROCESSING))
            }
        }

        return RouteAssignmentResult.SUCCESS
    }

    fun notifyCustomersForDeliveryDate(targetDate: LocalDate) {
        val orders = getOrdersForDeliveryDate(targetDate)

        orders.forEach { orderInfo ->
            try {
                notificationService.sendDeliveryNotification(
                    customerId = orderInfo.customerId,
                    orderNumber = orderInfo.orderNumber,
                    deliveryDate = orderInfo.deliveryDate
                )
            } catch (e: Exception) {
                // Log error but continue with other notifications
                println("Failed to send notification for order ${orderInfo.orderNumber}: ${e.message}")
            }
        }
    }

    fun getDeliveryStatistics(startDate: LocalDate, endDate: LocalDate): DeliveryStatistics {
        var currentDate = startDate
        var totalOrders = 0
        val dailyCounts = mutableMapOf<LocalDate, Int>()

        while (!currentDate.isAfter(endDate)) {
            val ordersForDate = getOrdersForDeliveryDate(currentDate)
            val count = ordersForDate.size
            dailyCounts[currentDate] = count
            totalOrders += count
            currentDate = currentDate.plusDays(1)
        }

        return DeliveryStatistics(
            totalOrders = totalOrders,
            dailyCounts = dailyCounts,
            averageOrdersPerDay = if (dailyCounts.isNotEmpty())
                totalOrders.toDouble() / dailyCounts.size else 0.0
        )
    }

    fun validateDeliverySchedule(targetDate: LocalDate): List<String> {
        val warnings = mutableListOf<String>()
        val orders = getOrdersForDeliveryDate(targetDate)

        if (orders.isEmpty()) {
            warnings.add("No orders scheduled for delivery on $targetDate")
        }

        if (orders.size > DeliveryConstants.MAX_ORDERS_PER_ROUTE) {
            warnings.add("Order count (${orders.size}) exceeds maximum route capacity")
        }

        val route = deliveryRouteRepository.findByDeliveryDate(targetDate).firstOrNull()
        if (route == null && orders.isNotEmpty()) {
            warnings.add("No delivery route assigned for date with ${orders.size} orders")
        }

        return warnings
    }
}

data class OrderDeliveryInfo(
    val orderId: Long,
    val orderNumber: String,
    val customerId: Long,
    val deliveryDate: LocalDateTime,
    val totalAmount: BigDecimal,
    val status: OrderStatus
)

data class DeliveryStatistics(
    val totalOrders: Int,
    val dailyCounts: Map<LocalDate, Int>,
    val averageOrdersPerDay: Double
)

enum class RouteAssignmentResult {
    SUCCESS, INVALID_DATE, CAPACITY_EXCEEDED
}

interface NotificationService {
    fun sendDeliveryNotification(customerId: Long, orderNumber: String, deliveryDate: LocalDateTime)
}
