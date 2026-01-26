package com.example.ecommerce.service;

import com.example.ecommerce.dto.OrderConfirmationDto;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.Customer;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.CustomerRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Optional;

@Service
@Transactional
public class OrderNotificationService {

    private static final Logger logger = LoggerFactory.getLogger(OrderNotificationService.class);
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    @Autowired
    private JavaMailSender mailSender;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private CustomerRepository customerRepository;

    @Value("${app.notification.from-email:noreply@example.com}")
    private String fromEmail;

    @Value("${app.notification.subject-prefix:Order Confirmation}")
    private String subjectPrefix;

    public void processOrderConfirmation(Long orderId) {
        logger.info("Processing order confirmation for order ID: {}", orderId);
        
        Optional<Order> orderOpt = orderRepository.findById(orderId);
        if (orderOpt.isEmpty()) {
            logger.warn("Order not found with ID: {}", orderId);
            return;
        }

        Order order = orderOpt.get();
        if (shouldSendConfirmation(order)) {
            OrderConfirmationDto confirmationDto = buildConfirmationDto(order);
            sendOrderConfirmationEmail(confirmationDto);
            updateOrderNotificationStatus(order);
        }
    }

    @Async
    public void sendOrderConfirmationEmail(OrderConfirmationDto confirmationDto) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(fromEmail);
        message.setTo(confirmationDto.getCustomerEmail());
        message.setSubject(buildEmailSubject(confirmationDto.getOrderNumber()));
        message.setText(buildEmailContent(confirmationDto));

        mailSender.send(message);
        logger.info("Order confirmation email sent successfully for order: {}", confirmationDto.getOrderNumber());
    }

    private boolean shouldSendConfirmation(Order order) {
        return order.getStatus().equals("CONFIRMED") && 
               !order.isNotificationSent() && 
               order.getCustomer() != null &&
               order.getCustomer().getEmail() != null;
    }

    private OrderConfirmationDto buildConfirmationDto(Order order) {
        Customer customer = order.getCustomer();
        OrderConfirmationDto dto = new OrderConfirmationDto();
        dto.setOrderNumber(order.getOrderNumber());
        dto.setCustomerName(customer.getFirstName() + " " + customer.getLastName());
        dto.setCustomerEmail(customer.getEmail());
        dto.setOrderDate(order.getCreatedAt());
        dto.setTotalAmount(order.getTotalAmount());
        dto.setShippingAddress(formatShippingAddress(order));
        return dto;
    }

    private String buildEmailSubject(String orderNumber) {
        return String.format("%s - Order #%s", subjectPrefix, orderNumber);
    }

    private String buildEmailContent(OrderConfirmationDto dto) {
        StringBuilder content = new StringBuilder();
        content.append("Dear ").append(dto.getCustomerName()).append(",\n\n");
        content.append("Thank you for your order! Here are the details:\n\n");
        content.append("Order Number: ").append(dto.getOrderNumber()).append("\n");
        content.append("Order Date: ").append(dto.getOrderDate().format(DATE_FORMATTER)).append("\n");
        content.append("Total Amount: $").append(dto.getTotalAmount()).append("\n");
        content.append("Shipping Address: ").append(dto.getShippingAddress()).append("\n\n");
        content.append("Your order will be processed within 1-2 business days.\n\n");
        content.append("Best regards,\nThe E-Commerce Team");
        return content.toString();
    }

    private String formatShippingAddress(Order order) {
        return String.format("%s, %s, %s %s", 
            order.getShippingStreet(),
            order.getShippingCity(),
            order.getShippingState(),
            order.getShippingZipCode());
    }

    private void updateOrderNotificationStatus(Order order) {
        order.setNotificationSent(true);
        order.setNotificationSentAt(LocalDateTime.now());
        orderRepository.save(order);
        logger.debug("Updated notification status for order: {}", order.getOrderNumber());
    }
}