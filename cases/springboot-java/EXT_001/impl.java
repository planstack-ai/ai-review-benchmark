package com.example.ecommerce.service;

import com.example.ecommerce.client.PaymentGatewayClient;
import com.example.ecommerce.dto.PaymentResponse;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.Payment;
import com.example.ecommerce.exception.PaymentException;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.PaymentRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;

import java.math.BigDecimal;
import java.net.http.HttpTimeoutException;
import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class PaymentProcessingService {

    private static final Logger logger = LoggerFactory.getLogger(PaymentProcessingService.class);

    @Autowired
    private PaymentGatewayClient paymentGatewayClient;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private PaymentRepository paymentRepository;

    @Transactional
    public Payment processPayment(Long orderId, String cardToken, BigDecimal amount) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        Payment payment = createPendingPayment(order, amount);
        paymentRepository.save(payment);

        try {
            PaymentResponse response = paymentGatewayClient.chargeCard(cardToken, amount);

            if (response.isSuccessful()) {
                payment.setStatus("COMPLETED");
                payment.setGatewayTransactionId(response.getTransactionId());
                payment.setProcessedAt(LocalDateTime.now());

                order.setStatus("PAID");
                order.setPaymentId(payment.getId());
                orderRepository.save(order);

                logger.info("Payment successful for order {}: {}", orderId, response.getTransactionId());
            } else {
                payment.setStatus("FAILED");
                payment.setFailureReason(response.getErrorMessage());

                order.setStatus("PAYMENT_FAILED");
                orderRepository.save(order);

                logger.warn("Payment failed for order {}: {}", orderId, response.getErrorMessage());
            }

        } catch (ResourceAccessException e) {
            if (e.getCause() instanceof HttpTimeoutException) {
                logger.error("Payment timeout for order {}", orderId);
                payment.setStatus("FAILED");
                payment.setFailureReason("Payment gateway timeout");
                order.setStatus("PAYMENT_FAILED");
                orderRepository.save(order);
                throw new PaymentException("Payment processing timeout - please try again", e);
            }
            throw new PaymentException("Payment processing error", e);
        } catch (HttpServerErrorException e) {
            logger.error("Payment gateway error for order {}: {}", orderId, e.getMessage());
            payment.setStatus("FAILED");
            payment.setFailureReason("Payment gateway error: " + e.getStatusCode());
            order.setStatus("PAYMENT_FAILED");
            orderRepository.save(order);
            throw new PaymentException("Payment gateway unavailable", e);
        }

        return paymentRepository.save(payment);
    }

    @Transactional
    public Payment retryPayment(Long orderId, String cardToken) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));

        if (!"PAYMENT_FAILED".equals(order.getStatus())) {
            throw new IllegalStateException("Order is not in PAYMENT_FAILED state");
        }

        return processPayment(orderId, cardToken, order.getTotalAmount());
    }

    private Payment createPendingPayment(Order order, BigDecimal amount) {
        Payment payment = new Payment();
        payment.setId(UUID.randomUUID().toString());
        payment.setOrderId(order.getId());
        payment.setAmount(amount);
        payment.setStatus("PENDING");
        payment.setCreatedAt(LocalDateTime.now());
        return payment;
    }
}
