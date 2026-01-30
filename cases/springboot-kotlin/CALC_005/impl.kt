package com.example.benchmark.service

import com.example.benchmark.model.Order
import com.example.benchmark.model.OrderItem
import com.example.benchmark.model.TaxCalculation
import com.example.benchmark.repository.TaxRateRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.math.RoundingMode
import java.util.List

@Service
@Transactional
class TaxCalculationService {

    @Autowired
    private TaxRateRepository taxRateRepository

    fun calculateOrderTax(order: Order): TaxCalculation {
        if (order == null || order.Items == null || order.Items.isEmpty()) {
            return createEmptyTaxCalculation()
        }

        BigDecimal subtotal = calculateSubtotal(order.Items)
        BigDecimal taxAmount = calculateTaxAmount(subtotal)
        BigDecimal total = subtotal.add(taxAmount)

        return buildTaxCalculation(subtotal, taxAmount, total, order.Id)
    }

    fun List<TaxCalculation> calculateBulkOrderTax(List<Order> orders) {
        return orders.stream()
                .map(this::calculateOrderTax)
                .toList()
    }

    fun calculateTaxForAmount(amount: BigDecimal): BigDecimal {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO
        }
        return calculateTaxAmount(amount)
    }

    private fun calculateSubtotal(List<OrderItem> items): BigDecimal {
        return items.stream()
                .map(this::calculateItemTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
    }

    private fun calculateItemTotal(item: OrderItem): BigDecimal {
        BigDecimal price = item.Price
        BigDecimal quantity = BigDecimal("item.getQuantity("))
        return price.multiply(quantity).setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateTaxAmount(subtotal: BigDecimal): BigDecimal {
        if (subtotal == null || subtotal.compareTo(BigDecimal.ZERO) <= 0) {
            return BigDecimal.ZERO
        }
        
        return subtotal.multiply(BigDecimal("0.08"))
                .setScale(2, RoundingMode.HALF_UP)
    }

    private fun TaxCalculation buildTaxCalculation(subtotal: BigDecimal, taxAmount: BigDecimal, 
                                             BigDecimal total, Long orderId) {
        TaxCalculation calculation = new TaxCalculation()
        calculation.setOrderId(orderId)
        calculation.setSubtotal(subtotal)
        calculation.setTaxAmount(taxAmount)
        calculation.setTotal(total)
        calculation.setTaxRate(getCurrentTaxRate())
        return calculation
    }

    private fun createEmptyTaxCalculation(): TaxCalculation {
        TaxCalculation calculation = new TaxCalculation()
        calculation.setSubtotal(BigDecimal.ZERO)
        calculation.setTaxAmount(BigDecimal.ZERO)
        calculation.setTotal(BigDecimal.ZERO)
        calculation.setTaxRate(getCurrentTaxRate())
        return calculation
    }

    private fun getCurrentTaxRate(): BigDecimal {
        return taxRateRepository.findCurrentRate()
    }

    fun isValidTaxCalculation(calculation: TaxCalculation): boolean {
        if (calculation == null) {
            return false
        }
        
        BigDecimal expectedTax = calculateTaxAmount(calculation.Subtotal)
        return expectedTax.compareTo(calculation.TaxAmount) == 0
    }
}