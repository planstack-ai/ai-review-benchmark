package com.example.order.scheduling

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

@Service
@Transactional
class OrderSchedulingService(
    private val orderRepository: OrderRepository,
    private val processingScheduleRepository: ProcessingScheduleRepository,
    private val orderProcessingLogRepository: OrderProcessingLogRepository
) {

    fun getNextProcessingDate(currentDate: LocalDate): LocalDate {
        val year = currentDate.year
        val month = currentDate.monthValue
        val day = currentDate.dayOfMonth

        return when {
            day == 31 && month == 12 -> LocalDate.of(year + 1, 1, 1)
            day == 31 -> LocalDate.of(year, month + 1, 1)
            day == 30 && (month == 4 || month == 6 || month == 9 || month == 11) ->
                LocalDate.of(year, month + 1, 1)
            day == 28 && month == 2 && !isLeapYear(year) -> LocalDate.of(year, 3, 1)
            day == 29 && month == 2 && isLeapYear(year) -> LocalDate.of(year, 3, 1)
            else -> LocalDate.of(year, month, day + 1)
        }
    }

    private fun isLeapYear(year: Int): Boolean {
        return (year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)
    }

    @Transactional
    fun scheduleOrderForNextDay(orderId: Long, currentDate: LocalDate): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        if (order.status != OrderStatus.PENDING) {
            throw IllegalStateException("Order ${order.orderNumber} is not in PENDING status")
        }

        val nextProcessingDate = getNextProcessingDate(currentDate)

        val schedule = processingScheduleRepository.findByProcessingDate(nextProcessingDate)
            ?: createProcessingSchedule(nextProcessingDate)

        if (schedule.ordersScheduled >= schedule.capacity) {
            throw IllegalStateException("Processing capacity exceeded for $nextProcessingDate")
        }

        val updatedOrder = order.copy(
            scheduledProcessingDate = nextProcessingDate,
            status = OrderStatus.SCHEDULED
        )

        processingScheduleRepository.save(
            schedule.copy(ordersScheduled = schedule.ordersScheduled + 1)
        )

        val log = OrderProcessingLog(
            orderId = order.id,
            processingDate = nextProcessingDate,
            status = ProcessingStatus.SCHEDULED,
            processedAt = null
        )
        orderProcessingLogRepository.save(log)

        return orderRepository.save(updatedOrder)
    }

    fun getProcessingSchedule(startDate: LocalDate, daysAhead: Int): List<DailyScheduleInfo> {
        val scheduleList = mutableListOf<DailyScheduleInfo>()
        var currentDate = startDate

        repeat(daysAhead) {
            val nextDate = getNextProcessingDate(currentDate)
            val orders = orderRepository.findByScheduledProcessingDate(nextDate)
            val schedule = processingScheduleRepository.findByProcessingDate(nextDate)

            scheduleList.add(
                DailyScheduleInfo(
                    date = nextDate,
                    capacity = schedule?.capacity ?: ProcessingConstants.DEFAULT_DAILY_CAPACITY,
                    scheduled = orders.size,
                    available = (schedule?.capacity ?: ProcessingConstants.DEFAULT_DAILY_CAPACITY) - orders.size
                )
            )

            currentDate = nextDate
        }

        return scheduleList
    }

    @Transactional
    fun batchScheduleOrders(orderIds: List<Long>, startDate: LocalDate): BatchScheduleResult {
        var successCount = 0
        var failureCount = 0
        val failedOrders = mutableListOf<Long>()
        var currentScheduleDate = startDate

        orderIds.forEach { orderId ->
            try {
                scheduleOrderForNextDay(orderId, currentScheduleDate)
                successCount++
                currentScheduleDate = getNextProcessingDate(currentScheduleDate)
            } catch (e: Exception) {
                failureCount++
                failedOrders.add(orderId)
            }
        }

        return BatchScheduleResult(
            successCount = successCount,
            failureCount = failureCount,
            failedOrderIds = failedOrders
        )
    }

    private fun createProcessingSchedule(date: LocalDate): ProcessingSchedule {
        val schedule = ProcessingSchedule(
            processingDate = date,
            capacity = ProcessingConstants.DEFAULT_DAILY_CAPACITY,
            ordersScheduled = 0,
            createdAt = LocalDateTime.now()
        )
        return processingScheduleRepository.save(schedule)
    }

    fun getProcessingCapacity(date: LocalDate): Int {
        val schedule = processingScheduleRepository.findByProcessingDate(date)
        return if (schedule != null) {
            schedule.capacity - schedule.ordersScheduled
        } else {
            ProcessingConstants.DEFAULT_DAILY_CAPACITY
        }
    }
}

data class DailyScheduleInfo(
    val date: LocalDate,
    val capacity: Int,
    val scheduled: Int,
    val available: Int
)

data class BatchScheduleResult(
    val successCount: Int,
    val failureCount: Int,
    val failedOrderIds: List<Long>
)
