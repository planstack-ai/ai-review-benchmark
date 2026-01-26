package com.example.service;

import com.example.dto.OrderRequest;
import com.example.dto.OrderResponse;
import com.example.entity.Order;
import com.example.entity.OrderItem;
import com.example.repository.OrderRepository;
import com.example.repository.ProductRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@Transactional
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private InventoryService inventoryService;

    @Autowired
    private PaymentService paymentService;

    public ResponseEntity<OrderResponse> createOrder(@RequestBody OrderRequest request) {
        if (!isValidCustomerId(request.getCustomerId())) {
            return ResponseEntity.badRequest().build();
        }

        Order order = buildOrderFromRequest(request);
        
        if (!validateOrderItems(order.getOrderItems())) {
            return ResponseEntity.status(HttpStatus.UNPROCESSABLE_ENTITY).build();
        }

        BigDecimal totalAmount = calculateOrderTotal(order.getOrderItems());
        order.setTotalAmount(totalAmount);
        order.setOrderDate(LocalDateTime.now());
        order.setStatus("PENDING");

        if (!reserveInventory(order.getOrderItems())) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }

        try {
            Order savedOrder = orderRepository.save(order);
            processPayment(savedOrder);
            
            OrderResponse response = convertToResponse(savedOrder);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (Exception e) {
            releaseInventoryReservation(order.getOrderItems());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    public ResponseEntity<OrderResponse> updateOrderStatus(Long orderId, String newStatus) {
        Optional<Order> orderOptional = orderRepository.findById(orderId);
        
        if (orderOptional.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        Order order = orderOptional.get();
        
        if (!isValidStatusTransition(order.getStatus(), newStatus)) {
            return ResponseEntity.badRequest().build();
        }

        order.setStatus(newStatus);
        order.setLastModified(LocalDateTime.now());
        
        Order updatedOrder = orderRepository.save(order);
        OrderResponse response = convertToResponse(updatedOrder);
        
        return ResponseEntity.ok(response);
    }

    private boolean isValidCustomerId(Long customerId) {
        return customerId != null && customerId > 0;
    }

    private Order buildOrderFromRequest(OrderRequest request) {
        Order order = new Order();
        order.setCustomerId(request.getCustomerId());
        order.setShippingAddress(request.getShippingAddress());
        order.setBillingAddress(request.getBillingAddress());
        
        List<OrderItem> orderItems = request.getItems().stream()
                .map(this::convertToOrderItem)
                .collect(Collectors.toList());
        
        order.setOrderItems(orderItems);
        return order;
    }

    private OrderItem convertToOrderItem(com.example.dto.OrderItemRequest itemRequest) {
        OrderItem orderItem = new OrderItem();
        orderItem.setProductId(itemRequest.getProductId());
        orderItem.setQuantity(itemRequest.getQuantity());
        orderItem.setUnitPrice(itemRequest.getUnitPrice());
        return orderItem;
    }

    private boolean validateOrderItems(List<OrderItem> orderItems) {
        return orderItems != null && !orderItems.isEmpty() &&
               orderItems.stream().allMatch(this::isValidOrderItem);
    }

    private boolean isValidOrderItem(OrderItem item) {
        return item.getProductId() != null && 
               item.getQuantity() > 0 && 
               item.getUnitPrice().compareTo(BigDecimal.ZERO) > 0;
    }

    private BigDecimal calculateOrderTotal(List<OrderItem> orderItems) {
        return orderItems.stream()
                .map(item -> item.getUnitPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private boolean reserveInventory(List<OrderItem> orderItems) {
        return inventoryService.reserveItems(orderItems);
    }

    private void releaseInventoryReservation(List<OrderItem> orderItems) {
        inventoryService.releaseReservation(orderItems);
    }

    private void processPayment(Order order) {
        paymentService.processPayment(order.getCustomerId(), order.getTotalAmount());
    }

    private boolean isValidStatusTransition(String currentStatus, String newStatus) {
        return !"CANCELLED".equals(currentStatus) && !"COMPLETED".equals(currentStatus);
    }

    private OrderResponse convertToResponse(Order order) {
        OrderResponse response = new OrderResponse();
        response.setOrderId(order.getId());
        response.setCustomerId(order.getCustomerId());
        response.setTotalAmount(order.getTotalAmount());
        response.setStatus(order.getStatus());
        response.setOrderDate(order.getOrderDate());
        return response;
    }
}