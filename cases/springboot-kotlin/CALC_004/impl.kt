package com.example.orderservice.service

import com.example.orderservice.model.Order
import com.example.orderservice.model.OrderItem
import com.example.orderservice.model.OrderTotal
import com.example.orderservice.repository.OrderRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.math.RoundingMode
import java.time.LocalDateTime

@Service
@Transactional
class OrderCalculationService(
    private val orderRepository: OrderRepository
) {

    fun calculateOrderTotal(orderId: Long): OrderTotal {
        val order = orderRepository.findById(orderId)
            ?: throw IllegalArgumentException("Order not found: $orderId")
        
        return calculateTotal(order)
    }

    fun processOrderCalculation(order: Order): Order {
        val total = calculateTotal(order)
        val updatedOrder = order.copy(
            total = total,
            lastCalculated = LocalDateTime.now()
        )
        return orderRepository.save(updatedOrder)
    }

    private fun calculateTotal(order: Order): OrderTotal {
        val subtotal = calculateSubtotal(order.items)
        val taxAmount = calculateTax(subtotal, order.taxRate)
        val shippingCost = calculateShipping(order)
        val discountAmount = calculateDiscount(order, subtotal)
        
        val finalTotal = subtotal
            .add(taxAmount)
            .add(shippingCost)
            .subtract(discountAmount)
            .setScale(2, RoundingMode.HALF_UP)

        return OrderTotal(
            subtotal = subtotal,
            taxAmount = taxAmount,
            shippingCost = shippingCost,
            discountAmount = discountAmount,
            total = finalTotal
        )
    }

    private fun calculateSubtotal(items: List<OrderItem>): BigDecimal {
        return if (items.isEmpty()) {
            BigDecimal.ZERO
        } else {
            items.map { calculateItemSubtotal(it).setScale(2, RoundingMode.HALF_UP) }
                .reduce(BigDecimal::add)
        }
    }

    private fun calculateItemSubtotal(item: OrderItem): BigDecimal {
        return item.unitPrice.multiply(BigDecimal.valueOf(item.quantity.toLong()))
    }

    private fun calculateTax(subtotal: BigDecimal, taxRate: BigDecimal): BigDecimal {
        return subtotal.multiply(taxRate)
            .setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateShipping(order: Order): BigDecimal {
        return when {
            order.subtotalThreshold != null && 
            order.total?.subtotal?.compareTo(order.subtotalThreshold) ?: -1 >= 0 -> BigDecimal.ZERO
            order.shippingMethod == "EXPRESS" -> BigDecimal("15.99")
            order.shippingMethod == "STANDARD" -> BigDecimal("7.99")
            else -> BigDecimal("5.99")
        }.setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateDiscount(order: Order, subtotal: BigDecimal): BigDecimal {
        val discountRate = order.discountRate ?: BigDecimal.ZERO
        return subtotal.multiply(discountRate)
            .setScale(2, RoundingMode.HALF_UP)
    }

    fun validateOrderCalculation(order: Order): Boolean {
        val calculatedTotal = calculateTotal(order)
        return order.total?.let { existingTotal ->
            existingTotal.total.compareTo(calculatedTotal.total) == 0
        } ?: false
    }
}