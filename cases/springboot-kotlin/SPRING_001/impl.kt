package com.example.ecommerce.service

import com.example.ecommerce.entity.Order
import com.example.ecommerce.entity.Payment
import com.example.ecommerce.entity.OrderStatus
import com.example.ecommerce.entity.PaymentStatus
import com.example.ecommerce.repository.OrderRepository
import com.example.ecommerce.repository.PaymentRepository
import com.example.ecommerce.exception.InsufficientFundsException
import com.example.ecommerce.exception.OrderProcessingException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.transaction.annotation.Propagation
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.*

@Service
class OrderProcessingService(
    private val orderRepository: OrderRepository,
    private val paymentRepository: PaymentRepository,
    private val paymentService: PaymentService,
    private val inventoryService: InventoryService,
    private val notificationService: NotificationService
) {

    @Transactional
    fun processOrder(customerId: Long, items: List<OrderItem>, paymentMethod: String): Order {
        val totalAmount = calculateTotalAmount(items)
        
        val order = createOrder(customerId, items, totalAmount)
        val savedOrder = orderRepository.save(order)
        
        try {
            reserveInventory(items)
            val payment = processPayment(savedOrder.id!!, totalAmount, paymentMethod)
            
            if (payment.status == PaymentStatus.COMPLETED) {
                savedOrder.status = OrderStatus.CONFIRMED
                savedOrder.confirmedAt = LocalDateTime.now()
                val confirmedOrder = orderRepository.save(savedOrder)
                
                scheduleNotifications(confirmedOrder)
                return confirmedOrder
            } else {
                throw OrderProcessingException("Payment processing failed")
            }
        } catch (exception: Exception) {
            savedOrder.status = OrderStatus.FAILED
            savedOrder.failureReason = exception.message
            orderRepository.save(savedOrder)
            throw exception
        }
    }

    private fun createOrder(customerId: Long, items: List<OrderItem>, totalAmount: BigDecimal): Order {
        return Order(
            customerId = customerId,
            items = items.toMutableList(),
            totalAmount = totalAmount,
            status = OrderStatus.PENDING,
            createdAt = LocalDateTime.now()
        )
    }

    private fun calculateTotalAmount(items: List<OrderItem>): BigDecimal {
        return items.fold(BigDecimal.ZERO) { total, item ->
            total.add(item.price.multiply(BigDecimal.valueOf(item.quantity.toLong())))
        }
    }

    private fun reserveInventory(items: List<OrderItem>) {
        items.forEach { item ->
            if (!inventoryService.reserveItem(item.productId, item.quantity)) {
                throw OrderProcessingException("Insufficient inventory for product ${item.productId}")
            }
        }
    }

    private fun processPayment(orderId: Long, amount: BigDecimal, paymentMethod: String): Payment {
        return paymentService.processPayment(orderId, amount, paymentMethod)
    }

    private fun scheduleNotifications(order: Order) {
        notificationService.scheduleOrderConfirmation(order.customerId, order.id!!)
    }

    @Transactional(readOnly = true)
    fun getOrderStatus(orderId: Long): OrderStatus? {
        return orderRepository.findById(orderId)?.status
    }

    @Transactional
    fun cancelOrder(orderId: Long): Boolean {
        val order = orderRepository.findById(orderId) ?: return false
        
        if (order.status == OrderStatus.CONFIRMED) {
            order.status = OrderStatus.CANCELLED
            order.cancelledAt = LocalDateTime.now()
            orderRepository.save(order)
            
            releaseInventory(order.items)
            refundPayment(orderId)
            return true
        }
        return false
    }

    private fun releaseInventory(items: List<OrderItem>) {
        items.forEach { item ->
            inventoryService.releaseItem(item.productId, item.quantity)
        }
    }

    private fun refundPayment(orderId: Long) {
        paymentService.refundPayment(orderId)
    }
}

@Service
class PaymentService(
    private val paymentRepository: PaymentRepository
) {

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun processPayment(orderId: Long, amount: BigDecimal, paymentMethod: String): Payment {
        val payment = Payment(
            orderId = orderId,
            amount = amount,
            paymentMethod = paymentMethod,
            status = PaymentStatus.PROCESSING,
            createdAt = LocalDateTime.now()
        )
        
        val savedPayment = paymentRepository.save(payment)
        
        val isSuccessful = executePaymentTransaction(amount, paymentMethod)
        
        savedPayment.status = if (isSuccessful) PaymentStatus.COMPLETED else PaymentStatus.FAILED
        savedPayment.processedAt = LocalDateTime.now()
        
        return paymentRepository.save(savedPayment)
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun refundPayment(orderId: Long) {
        val payment = paymentRepository.findByOrderId(orderId)
        payment?.let {
            it.status = PaymentStatus.REFUNDED
            it.refundedAt = LocalDateTime.now()
            paymentRepository.save(it)
        }
    }

    private fun executePaymentTransaction(amount: BigDecimal, paymentMethod: String): Boolean {
        return when (paymentMethod) {
            "CREDIT_CARD" -> processCreditCardPayment(amount)
            "DEBIT_CARD" -> processDebitCardPayment(amount)
            "BANK_TRANSFER" -> processBankTransfer(amount)
            else -> false
        }
    }

    private fun processCreditCardPayment(amount: BigDecimal): Boolean {
        return amount <= BigDecimal("10000")
    }

    private fun processDebitCardPayment(amount: BigDecimal): Boolean {
        return amount <= BigDecimal("5000")
    }

    private fun processBankTransfer(amount: BigDecimal): Boolean {
        return true
    }
}

data class OrderItem(
    val productId: Long,
    val quantity: Int,
    val price: BigDecimal
)