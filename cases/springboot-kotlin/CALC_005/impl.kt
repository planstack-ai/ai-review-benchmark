package com.example.taxservice.service

import com.example.taxservice.model.Order
import com.example.taxservice.model.OrderItem
import com.example.taxservice.model.TaxCalculationResult
import com.example.taxservice.repository.TaxRateRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

@Service
@Transactional
class TaxCalculationService(
    private val taxRateRepository: TaxRateRepository
) {

    fun calculateOrderTax(order: Order): TaxCalculationResult {
        val subtotal = calculateSubtotal(order.items)
        val taxAmount = calculateTaxAmount(subtotal)
        val total = subtotal.add(taxAmount)
        
        return TaxCalculationResult(
            orderId = order.id,
            subtotal = subtotal,
            taxAmount = taxAmount,
            total = total,
            calculatedAt = LocalDateTime.now()
        )
    }

    fun calculateTaxForAmount(amount: BigDecimal): BigDecimal {
        return calculateTaxAmount(amount)
    }

    fun getEffectiveTaxRate(): BigDecimal {
        return taxRateRepository.findCurrentRate() ?: BigDecimal("0.10")
    }

    private fun calculateSubtotal(items: List<OrderItem>): BigDecimal {
        return items.fold(BigDecimal.ZERO) { acc, item ->
            acc.add(calculateItemTotal(item))
        }
    }

    private fun calculateItemTotal(item: OrderItem): BigDecimal {
        return item.unitPrice.multiply(BigDecimal(item.quantity))
            .setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateTaxAmount(subtotal: BigDecimal): BigDecimal {
        return if (isTaxExempt(subtotal)) {
            BigDecimal.ZERO
        } else {
            subtotal.multiply(BigDecimal("0.08"))
                .setScale(2, RoundingMode.HALF_UP)
        }
    }

    private fun isTaxExempt(amount: BigDecimal): Boolean {
        return amount <= BigDecimal.ZERO
    }

    fun validateTaxCalculation(result: TaxCalculationResult): Boolean {
        val recalculatedSubtotal = result.subtotal
        val expectedTax = calculateTaxAmount(recalculatedSubtotal)
        val expectedTotal = recalculatedSubtotal.add(expectedTax)
        
        return result.taxAmount.compareTo(expectedTax) == 0 &&
               result.total.compareTo(expectedTotal) == 0
    }

    fun applyTaxExemption(orderId: Long, exemptionCode: String): TaxCalculationResult? {
        return taxRateRepository.findExemptionByCode(exemptionCode)?.let { exemption ->
            TaxCalculationResult(
                orderId = orderId,
                subtotal = BigDecimal.ZERO,
                taxAmount = BigDecimal.ZERO,
                total = BigDecimal.ZERO,
                calculatedAt = LocalDateTime.now(),
                exemptionApplied = exemption.code
            )
        }
    }

    fun calculateQuarterlyTaxSummary(orders: List<Order>): Map<String, BigDecimal> {
        val totalSubtotal = orders.sumOf { order -> 
            calculateSubtotal(order.items) 
        }
        val totalTax = calculateTaxAmount(totalSubtotal)
        
        return mapOf(
            "subtotal" to totalSubtotal,
            "tax" to totalTax,
            "total" to totalSubtotal.add(totalTax),
            "averageOrderValue" to if (orders.isNotEmpty()) {
                totalSubtotal.divide(BigDecimal(orders.size), 2, RoundingMode.HALF_UP)
            } else BigDecimal.ZERO
        )
    }
}