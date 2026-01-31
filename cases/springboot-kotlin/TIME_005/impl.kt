package com.example.subscription.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDate
import java.time.LocalDateTime

@Service
@Transactional
class SubscriptionBillingService(
    private val subscriptionRepository: SubscriptionRepository,
    private val billingHistoryRepository: BillingHistoryRepository,
    private val paymentService: PaymentService
) {

    fun calculateNextBillingDate(currentBillingDate: LocalDate): LocalDate {
        val year = currentBillingDate.year
        val month = currentBillingDate.monthValue
        val day = currentBillingDate.dayOfMonth

        val nextMonth = if (month == 12) 1 else month + 1
        val nextYear = if (month == 12) year + 1 else year

        return LocalDate.of(nextYear, nextMonth, day)
    }

    @Transactional
    fun processDueBillings(currentDate: LocalDate): BillingResult {
        val dueSubscriptions = subscriptionRepository.findByNextBillingDateLessThanEqual(currentDate)
            .filter { it.status == SubscriptionStatus.ACTIVE }

        var processedCount = 0
        var failedCount = 0
        var totalAmount = BigDecimal.ZERO

        dueSubscriptions.forEach { subscription ->
            try {
                val paymentResult = paymentService.processPayment(
                    customerId = subscription.customerId,
                    amount = subscription.monthlyAmount,
                    description = "Monthly subscription billing"
                )

                if (paymentResult.success) {
                    val billingHistory = BillingHistory(
                        subscriptionId = subscription.id,
                        billingDate = subscription.nextBillingDate,
                        amount = subscription.monthlyAmount,
                        status = BillingStatus.PROCESSED,
                        processedAt = LocalDateTime.now()
                    )
                    billingHistoryRepository.save(billingHistory)

                    val nextBilling = calculateNextBillingDate(subscription.nextBillingDate)
                    subscriptionRepository.save(
                        subscription.copy(
                            billingDate = subscription.nextBillingDate,
                            nextBillingDate = nextBilling,
                            updatedAt = LocalDateTime.now()
                        )
                    )

                    processedCount++
                    totalAmount = totalAmount.add(subscription.monthlyAmount)
                } else {
                    recordFailedBilling(subscription, paymentResult.errorMessage)
                    failedCount++
                }
            } catch (e: Exception) {
                recordFailedBilling(subscription, e.message ?: "Unknown error")
                failedCount++
            }
        }

        return BillingResult(
            processed = processedCount,
            failed = failedCount,
            totalAmount = totalAmount
        )
    }

    @Transactional
    fun createSubscription(customerId: Long, planId: Long, startDate: LocalDate): Subscription {
        val plan = subscriptionPlanRepository.findById(planId)
            .orElseThrow { IllegalArgumentException("Plan not found") }

        val nextBillingDate = calculateNextBillingDate(startDate)

        val subscription = Subscription(
            customerId = customerId,
            planId = planId,
            status = SubscriptionStatus.ACTIVE,
            billingDate = startDate,
            nextBillingDate = nextBillingDate,
            monthlyAmount = plan.monthlyPrice,
            createdAt = LocalDateTime.now(),
            updatedAt = LocalDateTime.now()
        )

        return subscriptionRepository.save(subscription)
    }

    fun getUpcomingBillings(daysAhead: Int): List<UpcomingBilling> {
        val endDate = LocalDate.now().plusDays(daysAhead.toLong())
        val subscriptions = subscriptionRepository.findByNextBillingDateLessThanEqual(endDate)
            .filter { it.status == SubscriptionStatus.ACTIVE }

        return subscriptions.map { subscription ->
            UpcomingBilling(
                subscriptionId = subscription.id,
                customerId = subscription.customerId,
                billingDate = subscription.nextBillingDate,
                amount = subscription.monthlyAmount,
                daysUntilBilling = java.time.temporal.ChronoUnit.DAYS.between(
                    LocalDate.now(),
                    subscription.nextBillingDate
                ).toInt()
            )
        }.sortedBy { it.billingDate }
    }

    private fun recordFailedBilling(subscription: Subscription, errorMessage: String?) {
        val billingHistory = BillingHistory(
            subscriptionId = subscription.id,
            billingDate = subscription.nextBillingDate,
            amount = subscription.monthlyAmount,
            status = BillingStatus.FAILED,
            processedAt = LocalDateTime.now()
        )
        billingHistoryRepository.save(billingHistory)

        // Log error for monitoring
        println("Billing failed for subscription ${subscription.id}: $errorMessage")
    }

    fun getBillingHistory(subscriptionId: Long): List<BillingHistoryInfo> {
        return billingHistoryRepository.findBySubscriptionIdOrderByBillingDateDesc(subscriptionId)
            .map { history ->
                BillingHistoryInfo(
                    billingDate = history.billingDate,
                    amount = history.amount,
                    status = history.status,
                    processedAt = history.processedAt
                )
            }
    }
}

data class UpcomingBilling(
    val subscriptionId: Long,
    val customerId: Long,
    val billingDate: LocalDate,
    val amount: BigDecimal,
    val daysUntilBilling: Int
)

data class BillingHistoryInfo(
    val billingDate: LocalDate,
    val amount: BigDecimal,
    val status: BillingStatus,
    val processedAt: LocalDateTime?
)

data class PaymentResult(
    val success: Boolean,
    val errorMessage: String?
)

interface PaymentService {
    fun processPayment(customerId: Long, amount: BigDecimal, description: String): PaymentResult
}

interface SubscriptionPlanRepository {
    fun findById(id: Long): java.util.Optional<SubscriptionPlan>
}
