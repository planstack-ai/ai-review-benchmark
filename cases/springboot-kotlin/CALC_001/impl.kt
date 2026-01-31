package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

@Service
@Transactional
class OrderDiscountService(
    private val membershipService: MembershipService,
    private val auditService: AuditService
) {

    fun calculateOrderTotal(customerId: Long, items: List<OrderItem>): OrderCalculationResult {
        val baseTotal = calculateBaseTotal(items)
        val isMember = membershipService.isMemberActive(customerId)
        
        return when {
            isMember -> applyMemberDiscount(customerId, baseTotal, items)
            else -> OrderCalculationResult(
                originalTotal = baseTotal,
                discountAmount = BigDecimal.ZERO,
                finalTotal = baseTotal,
                discountApplied = false
            )
        }
    }

    private fun applyMemberDiscount(customerId: Long, total: BigDecimal, items: List<OrderItem>): OrderCalculationResult {
        val eligibleItems = filterEligibleItems(items)
        val eligibleTotal = calculateEligibleTotal(eligibleItems)
        
        if (eligibleTotal <= BigDecimal.ZERO) {
            return OrderCalculationResult(
                originalTotal = total,
                discountAmount = BigDecimal.ZERO,
                finalTotal = total,
                discountApplied = false
            )
        }

        val discountAmount = calculateMemberDiscountAmount(eligibleTotal)
        val finalTotal = total.subtract(discountAmount)
        
        logDiscountApplication(customerId, total, discountAmount, finalTotal)
        
        return OrderCalculationResult(
            originalTotal = total,
            discountAmount = discountAmount,
            finalTotal = finalTotal,
            discountApplied = true
        )
    }

    private fun calculateMemberDiscountAmount(eligibleTotal: BigDecimal): BigDecimal {
        return eligibleTotal.multiply(BigDecimal("0.1"))
            .setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateBaseTotal(items: List<OrderItem>): BigDecimal {
        return items.fold(BigDecimal.ZERO) { acc, item ->
            acc.add(item.price.multiply(BigDecimal(item.quantity)))
        }
    }

    private fun filterEligibleItems(items: List<OrderItem>): List<OrderItem> {
        return items.filter { item ->
            !item.isGiftCard && !item.category.equals("ALCOHOL", ignoreCase = true)
        }
    }

    private fun calculateEligibleTotal(eligibleItems: List<OrderItem>): BigDecimal {
        return eligibleItems.fold(BigDecimal.ZERO) { acc, item ->
            acc.add(item.price.multiply(BigDecimal(item.quantity)))
        }
    }

    private fun logDiscountApplication(customerId: Long, originalTotal: BigDecimal, 
                                     discountAmount: BigDecimal, finalTotal: BigDecimal) {
        auditService.logDiscountEvent(
            customerId = customerId,
            discountType = "MEMBER_DISCOUNT",
            originalAmount = originalTotal,
            discountAmount = discountAmount,
            finalAmount = finalTotal,
            timestamp = LocalDateTime.now()
        )
    }
}

data class OrderItem(
    val id: Long,
    val name: String,
    val price: BigDecimal,
    val quantity: Int,
    val category: String,
    val isGiftCard: Boolean = false
)

data class OrderCalculationResult(
    val originalTotal: BigDecimal,
    val discountAmount: BigDecimal,
    val finalTotal: BigDecimal,
    val discountApplied: Boolean
)

interface MembershipService {
    fun isMemberActive(customerId: Long): Boolean
}

interface AuditService {
    fun logDiscountEvent(
        customerId: Long,
        discountType: String,
        originalAmount: BigDecimal,
        discountAmount: BigDecimal,
        finalAmount: BigDecimal,
        timestamp: LocalDateTime
    )
}