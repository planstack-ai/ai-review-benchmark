package com.example.ecommerce.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode

@Service
@Transactional
class ShippingCalculationService {

    companion object {
        private val STANDARD_SHIPPING_FEE = BigDecimal("500")
        private val EXPRESS_SHIPPING_FEE = BigDecimal("1200")
        private val FREE_SHIPPING_THRESHOLD = BigDecimal("5000")
        private val WEIGHT_MULTIPLIER = BigDecimal("0.1")
    }

    fun calculateShippingCost(orderTotal: BigDecimal, isExpress: Boolean = false, totalWeight: BigDecimal? = null): BigDecimal {
        val baseShippingFee = determineBaseShippingFee(isExpress)
        val weightAdjustment = calculateWeightAdjustment(totalWeight)
        val totalShippingFee = baseShippingFee.add(weightAdjustment)
        
        return applyFreeShippingPolicy(orderTotal, totalShippingFee)
    }

    private fun determineBaseShippingFee(isExpress: Boolean): BigDecimal {
        return if (isExpress) EXPRESS_SHIPPING_FEE else STANDARD_SHIPPING_FEE
    }

    private fun calculateWeightAdjustment(totalWeight: BigDecimal?): BigDecimal {
        return totalWeight?.let { weight ->
            if (weight > BigDecimal("10")) {
                weight.subtract(BigDecimal("10")).multiply(WEIGHT_MULTIPLIER)
            } else {
                BigDecimal.ZERO
            }
        } ?: BigDecimal.ZERO
    }

    private fun applyFreeShippingPolicy(orderTotal: BigDecimal, shippingFee: BigDecimal): BigDecimal {
        return if (orderTotal > FREE_SHIPPING_THRESHOLD) {
            BigDecimal.ZERO
        } else {
            shippingFee
        }
    }

    fun calculateTotalOrderCost(itemsTotal: BigDecimal, isExpress: Boolean = false, totalWeight: BigDecimal? = null): BigDecimal {
        val shippingCost = calculateShippingCost(itemsTotal, isExpress, totalWeight)
        return itemsTotal.add(shippingCost).setScale(2, RoundingMode.HALF_UP)
    }

    fun isEligibleForFreeShipping(orderTotal: BigDecimal): Boolean {
        return orderTotal >= FREE_SHIPPING_THRESHOLD
    }

    fun getShippingOptions(orderTotal: BigDecimal, totalWeight: BigDecimal?): Map<String, BigDecimal> {
        val standardCost = calculateShippingCost(orderTotal, false, totalWeight)
        val expressCost = calculateShippingCost(orderTotal, true, totalWeight)
        
        return mapOf(
            "standard" to standardCost,
            "express" to expressCost
        )
    }

    fun estimateDeliveryDays(isExpress: Boolean, orderTotal: BigDecimal): Int {
        return when {
            isExpress -> 1
            orderTotal >= FREE_SHIPPING_THRESHOLD -> 3
            else -> 5
        }
    }

    private fun validateOrderTotal(orderTotal: BigDecimal) {
        require(orderTotal >= BigDecimal.ZERO) { "Order total cannot be negative" }
    }

    fun calculateShippingDiscount(originalShipping: BigDecimal, orderTotal: BigDecimal): BigDecimal {
        validateOrderTotal(orderTotal)
        val discountedShipping = calculateShippingCost(orderTotal, false)
        return originalShipping.subtract(discountedShipping).max(BigDecimal.ZERO)
    }
}