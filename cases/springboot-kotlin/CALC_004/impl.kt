package com.example.ecommerce.service

import com.example.ecommerce.model.Order
import com.example.ecommerce.model.OrderItem
import com.example.ecommerce.repository.OrderRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.math.RoundingMode
import java.util.List
import java.util.Optional

@Service
@Transactional
class OrderCalculationService {

    @Autowired
    private OrderRepository orderRepository

    @Autowired
    private TaxCalculationService taxCalculationService

    @Autowired
    private DiscountService discountService

    fun calculateOrderTotal(orderId: Long): BigDecimal {
        Optional<Order> orderOpt = orderRepository.findById(orderId)
        if (orderOpt.isEmpty()) {
            throw new IllegalArgumentException("Order not found with id: " + orderId)
        }

        Order order = orderOpt.get()
        return calculateOrderTotal(order)
    }

    fun calculateOrderTotal(order: Order): BigDecimal {
        BigDecimal subtotal = calculateSubtotal(order.Items)
        BigDecimal discountAmount = discountService.calculateDiscount(order)
        BigDecimal taxableAmount = subtotal.subtract(discountAmount)
        BigDecimal taxAmount = taxCalculationService.calculateTax(taxableAmount, order.ShippingAddress)
        BigDecimal shippingCost = calculateShippingCost(order)
        
        return subtotal.subtract(discountAmount).add(taxAmount).add(shippingCost)
    }

    private fun calculateSubtotal(List<OrderItem> items): BigDecimal {
        if (items == null || items.isEmpty()) {
            return BigDecimal.ZERO
        }

        return items.stream()
                .map(item -> calculateItemSubtotal(item).setScale(2, RoundingMode.HALF_UP))
                .reduce(BigDecimal.ZERO, BigDecimal::add)
    }

    private fun calculateItemSubtotal(item: OrderItem): BigDecimal {
        BigDecimal unitPrice = item.UnitPrice
        BigDecimal quantity = BigDecimal(item.Quantity)
        return unitPrice.multiply(quantity)
    }

    private fun calculateShippingCost(order: Order): BigDecimal {
        BigDecimal baseShippingRate = BigDecimal("5.99")
        BigDecimal weightMultiplier = BigDecimal("0.50")
        
        BigDecimal totalWeight = order.Items.stream()
                .map(item -> item.Product.getWeight().multiply(BigDecimal(item.Quantity)))
                .reduce(BigDecimal.ZERO, BigDecimal::add)

        BigDecimal weightBasedCost = totalWeight.multiply(weightMultiplier)
        BigDecimal totalShipping = baseShippingRate.add(weightBasedCost)

        if (order.ShippingMethod.equals("EXPRESS")) {
            totalShipping = totalShipping.multiply(BigDecimal("1.5"))
        }

        return totalShipping.setScale(2, RoundingMode.HALF_UP)
    }

    @Transactional
    fun updateOrderTotals(orderId: Long): Order {
        Order order = orderRepository.findById(orderId)
                .orElseThrow { new IllegalArgumentException("Order not found" })

        BigDecimal calculatedTotal = calculateOrderTotal(order)
        order.setTotalAmount(calculatedTotal)
        
        return orderRepository.save(order)
    }

    fun validateOrderTotal(order: Order): boolean {
        BigDecimal calculatedTotal = calculateOrderTotal(order)
        BigDecimal storedTotal = order.TotalAmount
        
        if (storedTotal == null) {
            return false
        }
        
        return calculatedTotal.compareTo(storedTotal) == 0
    }

    private fun isEligibleForFreeShipping(order: Order): boolean {
        BigDecimal freeShippingThreshold = BigDecimal("75.00")
        BigDecimal subtotal = calculateSubtotal(order.Items)
        return subtotal.compareTo(freeShippingThreshold) >= 0
    }
}