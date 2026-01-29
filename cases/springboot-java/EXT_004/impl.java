package com.example.ecommerce.service;

import com.example.ecommerce.client.FulfillmentApiClient;
import com.example.ecommerce.dto.FulfillmentRequest;
import com.example.ecommerce.dto.FulfillmentResponse;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.repository.OrderRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.retry.annotation.Backoff;
import org.springframework.retry.annotation.Retryable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;

import java.time.LocalDateTime;

@Service
public class FulfillmentService {

    private static final Logger logger = LoggerFactory.getLogger(FulfillmentService.class);

    @Autowired
    private FulfillmentApiClient fulfillmentApiClient;

    @Autowired
    private OrderRepository orderRepository;

    @Retryable(
            retryFor = {RestClientException.class},
            maxAttempts = 3,
            backoff = @Backoff(delay = 1000, multiplier = 2)
    )
    public String submitOrderForFulfillment(Long orderId) {
        logger.info("Submitting order {} for fulfillment", orderId);

        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        FulfillmentRequest request = buildFulfillmentRequest(order);

        FulfillmentResponse response = fulfillmentApiClient.submitOrder(request);

        order.setFulfillmentId(response.getFulfillmentId());
        order.setStatus("SUBMITTED_FOR_FULFILLMENT");
        order.setSubmittedAt(LocalDateTime.now());
        orderRepository.save(order);

        logger.info("Order {} submitted successfully, fulfillment ID: {}",
                orderId, response.getFulfillmentId());

        return response.getFulfillmentId();
    }

    @Retryable(
            retryFor = {RestClientException.class},
            maxAttempts = 5,
            backoff = @Backoff(delay = 500, multiplier = 1.5)
    )
    public void createShipment(Order order) {
        logger.info("Creating shipment for order {}", order.getId());

        FulfillmentRequest request = new FulfillmentRequest();
        request.setOrderId(order.getId().toString());
        request.setCustomerId(order.getCustomerId());
        request.setShippingAddress(order.getShippingAddress());
        request.setItems(order.getItems());

        FulfillmentResponse response = fulfillmentApiClient.createShipment(request);

        order.setTrackingNumber(response.getTrackingNumber());
        order.setCarrier(response.getCarrier());
        order.setStatus("SHIPPED");
        orderRepository.save(order);
    }

    @Retryable(
            retryFor = {RestClientException.class},
            maxAttempts = 3,
            backoff = @Backoff(delay = 2000)
    )
    public void updateInventoryExternal(String productId, int quantity) {
        logger.info("Updating external inventory for product {}: {}", productId, quantity);

        fulfillmentApiClient.updateInventory(productId, quantity);

        logger.info("External inventory updated for product {}", productId);
    }

    private FulfillmentRequest buildFulfillmentRequest(Order order) {
        FulfillmentRequest request = new FulfillmentRequest();
        request.setOrderId(order.getId().toString());
        request.setCustomerId(order.getCustomerId());
        request.setShippingAddress(order.getShippingAddress());
        request.setItems(order.getItems());
        request.setPriority(determinePriority(order));
        return request;
    }

    private String determinePriority(Order order) {
        if (order.isExpressShipping()) {
            return "HIGH";
        }
        return "NORMAL";
    }
}
