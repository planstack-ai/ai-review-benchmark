package com.example.service

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

@Service
@Transactional
class OrderValidationService(
    private val orderRepository: OrderRepository,
    private val orderSettingsRepository: OrderSettingsRepository
) {

    fun validateMinimumOrderAmount(orderId: Long): ValidationResult {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val minimumAmount = getMinimumOrderAmount()

        return validateOrder(order, minimumAmount)
    }

    fun validateOrderBeforePayment(order: Order): ValidationResult {
        val minimumAmount = getMinimumOrderAmount()
        return validateOrder(order, minimumAmount)
    }

    private fun validateOrder(order: Order, minimumAmount: BigDecimal): ValidationResult {
        val orderAmount = order.subtotal

        return if (orderAmount >= minimumAmount) {
            ValidationResult(
                isValid = true,
                orderAmount = orderAmount,
                minimumAmount = minimumAmount,
                shortfall = BigDecimal.ZERO
            )
        } else {
            ValidationResult(
                isValid = false,
                orderAmount = orderAmount,
                minimumAmount = minimumAmount,
                shortfall = minimumAmount.subtract(orderAmount)
            )
        }
    }

    private fun getMinimumOrderAmount(): BigDecimal {
        return orderSettingsRepository.findBySettingKey(MINIMUM_ORDER_SETTING_KEY)
            ?.let { BigDecimal(it.settingValue) }
            ?: DEFAULT_MINIMUM_ORDER_AMOUNT
    }

    fun processOrderIfValid(orderId: Long): Order {
        val order = orderRepository.findById(orderId)
            .orElseThrow { IllegalArgumentException("Order not found: $orderId") }

        val validationResult = validateOrderBeforePayment(order)

        if (!validationResult.isValid) {
            throw MinimumOrderException(
                currentAmount = validationResult.orderAmount,
                minimumAmount = validationResult.minimumAmount
            )
        }

        order.status = OrderStatus.PENDING
        return orderRepository.save(order)
    }

    companion object {
        val DEFAULT_MINIMUM_ORDER_AMOUNT = BigDecimal("1000")
        const val MINIMUM_ORDER_SETTING_KEY = "minimum_order_amount"
    }
}

data class ValidationResult(
    val isValid: Boolean,
    val orderAmount: BigDecimal,
    val minimumAmount: BigDecimal,
    val shortfall: BigDecimal
)

data class Order(
    val id: Long = 0,
    val customerId: Long,
    val subtotal: BigDecimal,
    val discountAmount: BigDecimal = BigDecimal.ZERO,
    val shippingFee: BigDecimal = BigDecimal.ZERO,
    val finalAmount: BigDecimal,
    var status: OrderStatus
)

enum class OrderStatus {
    DRAFT, PENDING, CONFIRMED, PAID, SHIPPED, DELIVERED, CANCELLED
}

data class OrderSettings(
    val id: Long = 0,
    val settingKey: String,
    val settingValue: String
)

interface OrderRepository {
    fun findById(id: Long): java.util.Optional<Order>
    fun save(order: Order): Order
}

interface OrderSettingsRepository {
    fun findBySettingKey(key: String): OrderSettings?
}

class MinimumOrderException(
    val currentAmount: BigDecimal,
    val minimumAmount: BigDecimal
) : RuntimeException("Order amount $currentAmount is below minimum $minimumAmount")
