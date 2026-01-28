package com.example.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
@Transactional
public class OrderService {

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private InventoryService inventoryService;

    public OrderResponse createOrder(OrderRequest request) {
        validateOrderRequest(request);
        
        Order order = buildOrder(request);
        order.setStatus(OrderStatus.PENDING);
        order.setCreatedAt(LocalDateTime.now());
        
        if (!inventoryService.checkAvailability(request.getProductId(), request.getQuantity())) {
            throw new InsufficientInventoryException("Product not available in requested quantity");
        }
        
        Order savedOrder = orderRepository.save(order);
        
        PaymentResult paymentResult = paymentService.processPayment(
            savedOrder.getId(), 
            savedOrder.getTotalAmount(),
            request.getPaymentMethod()
        );
        
        if (paymentResult.isSuccessful()) {
            savedOrder.setStatus(OrderStatus.CONFIRMED);
            inventoryService.reserveItems(request.getProductId(), request.getQuantity());
        } else {
            savedOrder.setStatus(OrderStatus.FAILED);
            savedOrder.setFailureReason(paymentResult.getErrorMessage());
        }
        
        Order finalOrder = orderRepository.save(savedOrder);
        return mapToOrderResponse(finalOrder);
    }

    public void cancelOrder(String orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException("Order not found: " + orderId));
        
        if (order.getStatus() == OrderStatus.CONFIRMED) {
            paymentService.refundPayment(orderId, order.getTotalAmount());
            inventoryService.releaseReservation(order.getProductId(), order.getQuantity());
        }
        
        order.setStatus(OrderStatus.CANCELLED);
        order.setCancelledAt(LocalDateTime.now());
        orderRepository.save(order);
    }

    public OrderStatus getOrderStatus(String orderId) {
        return orderRepository.findById(orderId)
            .map(Order::getStatus)
            .orElseThrow(() -> new OrderNotFoundException("Order not found: " + orderId));
    }

    private void validateOrderRequest(OrderRequest request) {
        if (request.getProductId() == null || request.getProductId().trim().isEmpty()) {
            throw new InvalidOrderException("Product ID is required");
        }
        if (request.getQuantity() <= 0) {
            throw new InvalidOrderException("Quantity must be positive");
        }
        if (request.getUnitPrice().compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidOrderException("Unit price must be positive");
        }
    }

    private Order buildOrder(OrderRequest request) {
        Order order = new Order();
        order.setId(UUID.randomUUID().toString());
        order.setCustomerId(request.getCustomerId());
        order.setProductId(request.getProductId());
        order.setQuantity(request.getQuantity());
        order.setUnitPrice(request.getUnitPrice());
        order.setTotalAmount(calculateTotalAmount(request.getUnitPrice(), request.getQuantity()));
        return order;
    }

    private BigDecimal calculateTotalAmount(BigDecimal unitPrice, int quantity) {
        return unitPrice.multiply(BigDecimal.valueOf(quantity));
    }

    private OrderResponse mapToOrderResponse(Order order) {
        OrderResponse response = new OrderResponse();
        response.setOrderId(order.getId());
        response.setStatus(order.getStatus());
        response.setTotalAmount(order.getTotalAmount());
        response.setCreatedAt(order.getCreatedAt());
        return response;
    }
}