package com.example.ecommerce.service;

import com.example.ecommerce.dto.OrderDetailDto;
import com.example.ecommerce.dto.OrderItemDetailDto;
import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderItem;
import com.example.ecommerce.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class OrderDetailService {

    @Autowired
    private OrderRepository orderRepository;

    @Transactional(readOnly = true)
    public OrderDetailDto getOrderDetails(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found: " + orderId));

        OrderDetailDto dto = new OrderDetailDto();
        dto.setOrderId(order.getId());
        dto.setStatus(order.getStatus());
        dto.setCreatedAt(order.getCreatedAt());

        List<OrderItemDetailDto> itemDetails = order.getItems().stream()
                .map(this::mapToItemDetail)
                .collect(Collectors.toList());

        dto.setItems(itemDetails);
        dto.setTotalAmount(calculateTotal(order.getItems()));

        return dto;
    }

    private OrderItemDetailDto mapToItemDetail(OrderItem item) {
        OrderItemDetailDto dto = new OrderItemDetailDto();
        dto.setProductId(item.getProductId());
        dto.setProductName(item.getProduct().getName());
        dto.setUnitPrice(item.getProduct().getPriceCents());
        dto.setQuantity(item.getQuantity());
        dto.setLineTotal(item.getProduct().getPriceCents() * item.getQuantity());
        return dto;
    }

    @Transactional(readOnly = true)
    public List<OrderDetailDto> getOrderHistory(Long userId) {
        List<Order> orders = orderRepository.findByUserIdOrderByCreatedAtDesc(userId);

        return orders.stream()
                .map(order -> {
                    OrderDetailDto dto = new OrderDetailDto();
                    dto.setOrderId(order.getId());
                    dto.setStatus(order.getStatus());
                    dto.setCreatedAt(order.getCreatedAt());

                    List<OrderItemDetailDto> items = order.getItems().stream()
                            .map(item -> {
                                OrderItemDetailDto itemDto = new OrderItemDetailDto();
                                itemDto.setProductId(item.getProductId());
                                itemDto.setProductName(item.getProduct().getName());
                                itemDto.setUnitPrice(item.getProduct().getPriceCents());
                                itemDto.setQuantity(item.getQuantity());
                                return itemDto;
                            })
                            .collect(Collectors.toList());

                    dto.setItems(items);
                    dto.setTotalAmount(calculateTotal(order.getItems()));
                    return dto;
                })
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public byte[] generateInvoice(Long orderId) {
        Order order = orderRepository.findById(orderId)
                .orElseThrow(() -> new IllegalArgumentException("Order not found"));

        StringBuilder invoice = new StringBuilder();
        invoice.append("INVOICE\n");
        invoice.append("Order #: ").append(order.getId()).append("\n");
        invoice.append("Date: ").append(order.getCreatedAt()).append("\n\n");
        invoice.append("Items:\n");

        for (OrderItem item : order.getItems()) {
            invoice.append(String.format("- %s x%d @ $%.2f = $%.2f\n",
                    item.getProduct().getName(),
                    item.getQuantity(),
                    item.getProduct().getPriceCents() / 100.0,
                    (item.getProduct().getPriceCents() * item.getQuantity()) / 100.0));
        }

        invoice.append("\nTotal: $").append(calculateTotal(order.getItems()) / 100.0);

        return invoice.toString().getBytes();
    }

    private long calculateTotal(List<OrderItem> items) {
        return items.stream()
                .mapToLong(item -> (long) item.getProduct().getPriceCents() * item.getQuantity())
                .sum();
    }
}
