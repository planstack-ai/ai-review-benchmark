package com.example.ecommerce.service;

import com.example.ecommerce.dto.OrderRequest;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderItem;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.OrderItemRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
public class OrderProcessingService {

    private static final Logger logger = LoggerFactory.getLogger(OrderProcessingService.class);

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private OrderItemRepository orderItemRepository;

    @Autowired
    private InventoryService inventoryService;

    @Autowired
    private PaymentGatewayService paymentGatewayService;

    @Autowired
    private ShippingService shippingService;

    @Autowired
    private NotificationService notificationService;

    @Transactional
    public Order processOrder(OrderRequest request) {
        logger.info("Processing order for customer: {}", request.getCustomerId());

        Order order = createOrder(request);
        order = orderRepository.save(order);

        List<OrderItem> items = createOrderItems(order, request);
        orderItemRepository.saveAll(items);

        inventoryService.reserveStock(request.getItems());

        BigDecimal totalAmount = calculateTotal(items);
        String transactionId = paymentGatewayService.chargeCard(
                request.getPaymentToken(),
                totalAmount
        );

        order.setPaymentTransactionId(transactionId);
        order.setStatus("PAID");

        String trackingNumber = shippingService.createShipment(order);
        order.setTrackingNumber(trackingNumber);
        order.setStatus("PROCESSING");

        orderRepository.save(order);

        notificationService.sendOrderConfirmation(request.getCustomerId(), order.getId());

        logger.info("Order processed successfully: {}", order.getId());
        return order;
    }

    @Transactional
    public Order createOrderWithPayment(OrderRequest request) {
        Order order = createOrder(request);
        order = orderRepository.save(order);

        List<OrderItem> items = createOrderItems(order, request);
        orderItemRepository.saveAll(items);

        BigDecimal total = calculateTotal(items);

        String paymentId = paymentGatewayService.chargeCard(request.getPaymentToken(), total);
        order.setPaymentTransactionId(paymentId);

        inventoryService.decrementStock(request.getItems());

        order.setStatus("COMPLETED");
        return orderRepository.save(order);
    }

    private Order createOrder(OrderRequest request) {
        Order order = new Order();
        order.setId(UUID.randomUUID().toString());
        order.setCustomerId(request.getCustomerId());
        order.setStatus("PENDING");
        order.setCreatedAt(LocalDateTime.now());
        return order;
    }

    private List<OrderItem> createOrderItems(Order order, OrderRequest request) {
        return request.getItems().stream()
                .map(itemReq -> {
                    OrderItem item = new OrderItem();
                    item.setOrderId(order.getId());
                    item.setProductId(itemReq.getProductId());
                    item.setQuantity(itemReq.getQuantity());
                    item.setPriceCents(itemReq.getPriceCents());
                    return item;
                })
                .toList();
    }

    private BigDecimal calculateTotal(List<OrderItem> items) {
        return items.stream()
                .map(item -> BigDecimal.valueOf(item.getPriceCents() * item.getQuantity()))
                .reduce(BigDecimal.ZERO, BigDecimal::add)
                .divide(BigDecimal.valueOf(100));
    }
}
