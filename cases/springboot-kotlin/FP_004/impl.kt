package com.example.orderservice.service

import com.example.orderservice.entity.Order
import com.example.orderservice.entity.OrderStatus
import com.example.orderservice.entity.OrderStatusTransition
import com.example.orderservice.repository.OrderRepository
import com.example.orderservice.repository.OrderStatusTransitionRepository
import com.example.orderservice.constants.OrderConstants
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.util.List
import java.util.Optional
import java.util.Set
import java.util.stream.Collectors

@Service
@Transactional
class OrderServiceImpl {

        private val orderRepository: OrderRepository
        private val transitionRepository: OrderStatusTransitionRepository

    @Autowired
    fun OrderServiceImpl(orderRepository: OrderRepository, 
                           OrderStatusTransitionRepository transitionRepository) {
        orderRepository = orderRepository
        transitionRepository = transitionRepository
    }

    @Override
    fun createOrder(customerId: Long, totalAmount: BigDecimal): Order {
        validateOrderCreationInput(customerId, totalAmount)
        
        Order order = new Order()
        order.setCustomerId(customerId)
        order.setTotalAmount(totalAmount)
        order.setStatus(OrderStatus.PENDING)
        
        return orderRepository.save(order)
    }

    @Override
    fun updateOrderStatus(orderId: Long, newStatus: OrderStatus): Order {
        Order order = findOrderById(orderId)
        OrderStatus currentStatus = order.Status
        
        validateStatusTransition(currentStatus, newStatus)
        
        order.setStatus(newStatus)
        return orderRepository.save(order)
    }

    @Override
    fun List<OrderStatus> getAllowedTransitions(currentStatus: OrderStatus) {
        List<OrderStatusTransition> transitions = transitionRepository
            .findByFromStatusAndAllowedTrue(currentStatus)
        
        if (transitions.isEmpty()) {
            return getDefaultAllowedTransitions(currentStatus)
        }
        
        return transitions.stream()
            .map(OrderStatusTransition::getToStatus)
            .collect(Collectors.toList())
    }

    @Override
    fun isTransitionAllowed(fromStatus: OrderStatus, toStatus: OrderStatus): boolean {
        Optional<OrderStatusTransition> transition = transitionRepository
            .findByFromStatusAndToStatus(fromStatus, toStatus)
        
        if (transition.isPresent()) {
            return transition.get().getAllowed()
        }
        
        return isDefaultTransitionAllowed(fromStatus, toStatus)
    }

    private fun validateOrderCreationInput(customerId: Long, totalAmount: BigDecimal): {
        if (customerId == null || customerId <= 0) {
            throw new IllegalArgumentException("Customer ID must be positive")
        }
        if (totalAmount == null || totalAmount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Total amount cannot be negative")
        }
    }

    private fun findOrderById(orderId: Long): Order {
        return orderRepository.findById(orderId)
            .orElseThrow { new IllegalArgumentException("Order not found with ID: " + orderId })
    }

    private fun validateStatusTransition(fromStatus: OrderStatus, toStatus: OrderStatus): {
        if (!isTransitionAllowed(fromStatus, toStatus)) {
            throw new IllegalStateException(
                String.format("Invalid status transition from %s to %s", fromStatus, toStatus))
        }
    }

    private fun List<OrderStatus> getDefaultAllowedTransitions(currentStatus: OrderStatus) {
        Set<OrderStatus> allowedStatuses = OrderConstants.DEFAULT_TRANSITIONS.get(currentStatus)
        return allowedStatuses != null ? 
            allowedStatuses.stream().collect(Collectors.toList()) : 
            List.of()
    }

    private fun isDefaultTransitionAllowed(fromStatus: OrderStatus, toStatus: OrderStatus): boolean {
        Set<OrderStatus> allowedTransitions = OrderConstants.DEFAULT_TRANSITIONS.get(fromStatus)
        return allowedTransitions != null && allowedTransitions.contains(toStatus)
    }
}