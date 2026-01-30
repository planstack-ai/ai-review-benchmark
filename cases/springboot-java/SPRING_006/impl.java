package com.example.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * Order processing service.
 * Handles order creation, cancellation, and status management.
 */
@Service
@Transactional
public class OrderService {

    // BUG: Circular dependency - OrderService depends on PaymentService
    @Autowired
    private PaymentService paymentService;

    @Autowired
    private OrderRepository orderRepository;

    public OrderResponse createOrder(OrderRequest request) {
        validateOrderRequest(request);

        Order order = new Order();
        order.setCustomerId(request.getCustomerId());
        order.setTotalAmount(request.getTotalAmount());
        order.setStatus(OrderStatus.PENDING);
        order.setCreatedAt(LocalDateTime.now());

        Order savedOrder = orderRepository.save(order);

        PaymentResult paymentResult = paymentService.processPayment(
            savedOrder.getId(),
            savedOrder.getTotalAmount(),
            request.getPaymentMethod()
        );

        if (paymentResult.isSuccessful()) {
            savedOrder.setStatus(OrderStatus.CONFIRMED);
        } else {
            savedOrder.setStatus(OrderStatus.CANCELLED);
        }

        return mapToOrderResponse(orderRepository.save(savedOrder));
    }

    public void cancelOrder(Long orderId) {
        Order order = orderRepository.findById(orderId)
            .orElseThrow(() -> new OrderNotFoundException("Order not found: " + orderId));

        if (order.getStatus() == OrderStatus.CONFIRMED) {
            paymentService.refundPayment(orderId, order.getTotalAmount());
        }

        order.setStatus(OrderStatus.CANCELLED);
        orderRepository.save(order);
    }

    public OrderStatus getOrderStatus(Long orderId) {
        return orderRepository.findById(orderId)
            .map(Order::getStatus)
            .orElseThrow(() -> new OrderNotFoundException("Order not found: " + orderId));
    }

    private void validateOrderRequest(OrderRequest request) {
        if (request.getCustomerId() == null) {
            throw new InvalidOrderException("Customer ID is required");
        }
        if (request.getTotalAmount() == null || request.getTotalAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new InvalidOrderException("Total amount must be positive");
        }
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

/**
 * Payment processing service.
 * Handles payment processing and refunds.
 */
@Service
@Transactional
class PaymentService {

    // BUG: Circular dependency - PaymentService depends on OrderService
    @Autowired
    private OrderService orderService;

    @Autowired
    private PaymentRepository paymentRepository;

    public PaymentResult processPayment(Long orderId, BigDecimal amount, PaymentMethod method) {
        // Verify order exists via OrderService (causes circular dependency)
        OrderStatus status = orderService.getOrderStatus(orderId);
        if (status != OrderStatus.PENDING) {
            return new PaymentResult(false, "Order is not in pending status");
        }

        Payment payment = new Payment();
        payment.setOrderId(orderId);
        payment.setAmount(amount);
        payment.setPaymentMethod(method);
        payment.setStatus(PaymentStatus.PROCESSING);

        try {
            // Simulate payment gateway call
            boolean gatewaySuccess = processWithGateway(amount, method);

            if (gatewaySuccess) {
                payment.setStatus(PaymentStatus.COMPLETED);
                payment.setProcessedAt(LocalDateTime.now());
                paymentRepository.save(payment);
                return new PaymentResult(true, null);
            } else {
                payment.setStatus(PaymentStatus.FAILED);
                paymentRepository.save(payment);
                return new PaymentResult(false, "Payment gateway rejected the transaction");
            }
        } catch (Exception e) {
            payment.setStatus(PaymentStatus.FAILED);
            paymentRepository.save(payment);
            return new PaymentResult(false, "Payment processing error: " + e.getMessage());
        }
    }

    public void refundPayment(Long orderId, BigDecimal amount) {
        Payment payment = paymentRepository.findByOrderIdAndStatus(orderId, PaymentStatus.COMPLETED)
            .orElseThrow(() -> new PaymentNotFoundException("No completed payment found for order: " + orderId));

        payment.setStatus(PaymentStatus.REFUNDED);
        paymentRepository.save(payment);
    }

    private boolean processWithGateway(BigDecimal amount, PaymentMethod method) {
        // Simplified gateway simulation
        return amount.compareTo(new BigDecimal("10000")) < 0;
    }
}