package com.example.orderservice.service;

import com.example.orderservice.entity.Order;
import com.example.orderservice.entity.OrderStatus;
import com.example.orderservice.entity.OrderStatusTransition;
import com.example.orderservice.repository.OrderRepository;
import com.example.orderservice.repository.OrderStatusTransitionRepository;
import com.example.orderservice.constants.OrderConstants;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

@Service
@Transactional
public class OrderServiceImpl implements OrderService {

    private final OrderRepository orderRepository;
    private final OrderStatusTransitionRepository transitionRepository;

    @Autowired
    public OrderServiceImpl(OrderRepository orderRepository, 
                           OrderStatusTransitionRepository transitionRepository) {
        this.orderRepository = orderRepository;
        this.transitionRepository = transitionRepository;
    }

    @Override
    public Order createOrder(Long customerId, BigDecimal totalAmount) {
        validateOrderCreationInput(customerId, totalAmount);
        
        Order order = new Order();
        order.setCustomerId(customerId);
        order.setTotalAmount(totalAmount);
        order.setStatus(OrderStatus.PENDING);
        
        return orderRepository.save(order);
    }

    @Override
    public Order updateOrderStatus(Long orderId, OrderStatus newStatus) {
        Order order = findOrderById(orderId);
        OrderStatus currentStatus = order.getStatus();
        
        validateStatusTransition(currentStatus, newStatus);
        
        order.setStatus(newStatus);
        return orderRepository.save(order);
    }

    @Override
    public List<OrderStatus> getAllowedTransitions(OrderStatus currentStatus) {
        List<OrderStatusTransition> transitions = transitionRepository
            .findByFromStatusAndAllowedTrue(currentStatus);
        
        if (transitions.isEmpty()) {
            return getDefaultAllowedTransitions(currentStatus);
        }
        
        return transitions.stream()
            .map(OrderStatusTransition::getToStatus)
            .collect(Collectors.toList());
    }

    @Override
    public boolean isTransitionAllowed(OrderStatus fromStatus, OrderStatus toStatus) {
        Optional<OrderStatusTransition> transition = transitionRepository
            .findByFromStatusAndToStatus(fromStatus, toStatus);
        
        if (transition.isPresent()) {
            return transition.get().getAllowed();
        }
        
        return isDefaultTransitionAllowed(fromStatus, toStatus);
    }

    private void validateOrderCreationInput(Long customerId, BigDecimal totalAmount) {
        if (customerId == null || customerId <= 0) {
            throw new IllegalArgumentException("Customer ID must be positive");
        }
        if (totalAmount == null || totalAmount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Total amount cannot be negative");
        }
    }

    private Order findOrderById(Long orderId) {
        return orderRepository.findById(orderId)
            .orElseThrow(() -> new IllegalArgumentException("Order not found with ID: " + orderId));
    }

    private void validateStatusTransition(OrderStatus fromStatus, OrderStatus toStatus) {
        if (!isTransitionAllowed(fromStatus, toStatus)) {
            throw new IllegalStateException(
                String.format("Invalid status transition from %s to %s", fromStatus, toStatus));
        }
    }

    private List<OrderStatus> getDefaultAllowedTransitions(OrderStatus currentStatus) {
        Set<OrderStatus> allowedStatuses = OrderConstants.DEFAULT_TRANSITIONS.get(currentStatus);
        return allowedStatuses != null ? 
            allowedStatuses.stream().collect(Collectors.toList()) : 
            List.of();
    }

    private boolean isDefaultTransitionAllowed(OrderStatus fromStatus, OrderStatus toStatus) {
        Set<OrderStatus> allowedTransitions = OrderConstants.DEFAULT_TRANSITIONS.get(fromStatus);
        return allowedTransitions != null && allowedTransitions.contains(toStatus);
    }
}