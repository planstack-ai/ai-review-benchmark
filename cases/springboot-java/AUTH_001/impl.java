package com.example.ecommerce.service;

import com.example.ecommerce.dto.OrderDetailsDto;
import com.example.ecommerce.dto.OrderSummaryDto;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderItem;
import com.example.ecommerce.entity.User;
import com.example.ecommerce.exception.OrderNotFoundException;
import com.example.ecommerce.exception.UnauthorizedException;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private UserRepository userRepository;

    public Page<OrderSummaryDto> getUserOrders(Pageable pageable) {
        User currentUser = getCurrentUser();
        Page<Order> orders = orderRepository.findByUserIdOrderByCreatedAtDesc(currentUser.getId(), pageable);
        return orders.map(this::convertToOrderSummary);
    }

    public OrderDetailsDto getOrderDetails(Long orderId) {
        User currentUser = getCurrentUser();
        validateUserAccess(currentUser);
        
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new OrderNotFoundException("Order not found with id: " + orderId));
        
        return convertToOrderDetails(order);
    }

    public List<OrderSummaryDto> getRecentOrders(int limit) {
        User currentUser = getCurrentUser();
        List<Order> recentOrders = orderRepository.findTop10ByUserIdOrderByCreatedAtDesc(currentUser.getId());
        return recentOrders.stream()
                .limit(limit)
                .map(this::convertToOrderSummary)
                .collect(Collectors.toList());
    }

    public BigDecimal calculateOrderTotal(Long orderId) {
        User currentUser = getCurrentUser();
        Order order = orderRepository.findByIdAndUserId(orderId, currentUser.getId())
                .orElseThrow(() -> new OrderNotFoundException("Order not found"));
        
        return calculateTotalAmount(order);
    }

    private User getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        String username = authentication.getName();
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new UnauthorizedException("User not found"));
    }

    private void validateUserAccess(User user) {
        if (user == null || !user.isActive()) {
            throw new UnauthorizedException("Access denied");
        }
    }

    private OrderSummaryDto convertToOrderSummary(Order order) {
        OrderSummaryDto dto = new OrderSummaryDto();
        dto.setId(order.getId());
        dto.setOrderNumber(order.getOrderNumber());
        dto.setStatus(order.getStatus());
        dto.setCreatedAt(order.getCreatedAt());
        dto.setTotalAmount(calculateTotalAmount(order));
        dto.setItemCount(order.getOrderItems().size());
        return dto;
    }

    private OrderDetailsDto convertToOrderDetails(Order order) {
        OrderDetailsDto dto = new OrderDetailsDto();
        dto.setId(order.getId());
        dto.setOrderNumber(order.getOrderNumber());
        dto.setStatus(order.getStatus());
        dto.setCreatedAt(order.getCreatedAt());
        dto.setShippingAddress(order.getShippingAddress());
        dto.setBillingAddress(order.getBillingAddress());
        dto.setTotalAmount(calculateTotalAmount(order));
        dto.setOrderItems(order.getOrderItems().stream()
                .map(this::convertOrderItem)
                .collect(Collectors.toList()));
        return dto;
    }

    private OrderDetailsDto.OrderItemDto convertOrderItem(OrderItem item) {
        OrderDetailsDto.OrderItemDto dto = new OrderDetailsDto.OrderItemDto();
        dto.setProductName(item.getProductName());
        dto.setQuantity(item.getQuantity());
        dto.setUnitPrice(item.getUnitPrice());
        dto.setSubtotal(item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())));
        return dto;
    }

    private BigDecimal calculateTotalAmount(Order order) {
        return order.getOrderItems().stream()
                .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}