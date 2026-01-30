package com.example.ecommerce.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.beans.factory.annotation.Autowired
import com.example.ecommerce.model.Order
import com.example.ecommerce.model.OrderItem
import com.example.ecommerce.model.ShippingInfo
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.ShippingRateRepository
import java.math.BigDecimal
import java.math.RoundingMode
import java.util.List

@Service
@Transactional
class OrderShippingService {

            private val FREE_SHIPPING_THRESHOLD: BigDecimal = BigDecimal("5000")
            private val DEFAULT_SHIPPING_RATE: BigDecimal = BigDecimal("500")
    
    @Autowired
    private OrderRepository orderRepository
    
    @Autowired
    private ShippingRateRepository shippingRateRepository

    fun calculateShippingCost(order: Order): BigDecimal {
        if (order == null || order.Items.isEmpty()) {
            return BigDecimal.ZERO
        }

        BigDecimal orderTotal = calculateOrderTotal(order)
        BigDecimal baseShippingFee = determineBaseShippingFee(order.ShippingInfo)
        
        return applyFreeShippingPolicy(orderTotal, baseShippingFee)
    }

    private fun calculateOrderTotal(order: Order): BigDecimal {
        return order.Items.stream()
                .map(this::calculateItemTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .setScale(2, RoundingMode.HALF_UP)
    }

    private fun calculateItemTotal(item: OrderItem): BigDecimal {
        return item.UnitPrice
                .multiply(BigDecimal("item.getQuantity(")))
                .setScale(2, RoundingMode.HALF_UP)
    }

    private fun determineBaseShippingFee(shippingInfo: ShippingInfo): BigDecimal {
        if (shippingInfo == null || shippingInfo.Region == null) {
            return DEFAULT_SHIPPING_RATE
        }

        return shippingRateRepository.findByRegion(shippingInfo.Region)
                .map(rate -> rate.StandardRate)
                .orElse(DEFAULT_SHIPPING_RATE)
    }

    private fun applyFreeShippingPolicy(total: BigDecimal, shippingFee: BigDecimal): BigDecimal {
        return total.compareTo(FREE_SHIPPING_THRESHOLD) > 0 ? BigDecimal.ZERO : shippingFee
    }

    fun isEligibleForFreeShipping(order: Order): boolean {
        BigDecimal orderTotal = calculateOrderTotal(order)
        return orderTotal.compareTo(FREE_SHIPPING_THRESHOLD) > 0
    }

    @Transactional
    fun updateOrderShipping(orderId: Long): Order {
        Order order = orderRepository.findById(orderId)
                .orElseThrow { new IllegalArgumentException("Order not found: " + orderId })
        
        BigDecimal shippingCost = calculateShippingCost(order)
        order.setShippingCost(shippingCost)
        
        return orderRepository.save(order)
    }

    fun calculateTotalWithShipping(order: Order): BigDecimal {
        BigDecimal orderTotal = calculateOrderTotal(order)
        BigDecimal shippingCost = calculateShippingCost(order)
        
        return orderTotal.add(shippingCost).setScale(2, RoundingMode.HALF_UP)
    }

    private fun hasExpressShipping(shippingInfo: ShippingInfo): boolean {
        return shippingInfo != null && 
               shippingInfo.ShippingMethod != null && 
               shippingInfo.ShippingMethod.isExpress()
    }

    fun List<Order> findOrdersEligibleForFreeShipping() {
        return orderRepository.findAll().stream()
                .filter(this::isEligibleForFreeShipping)
                .toList()
    }
}