package com.example.benchmark.service;

import com.example.benchmark.entity.Order;
import com.example.benchmark.entity.OrderItem;
import com.example.benchmark.repository.OrderRepository;
import com.example.benchmark.dto.OrderSummaryDto;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@Transactional
public class OrderAnalysisService {

    @Autowired
    private OrderRepository orderRepository;

    public List<OrderSummaryDto> generateOrderSummaryReport() {
        List<Order> orders = orderRepository.findAll();
        return orders.stream()
                .map(this::createOrderSummary)
                .collect(Collectors.toList());
    }

    public BigDecimal calculateTotalRevenue() {
        List<Order> orders = orderRepository.findAll();
        return orders.stream()
                .map(this::calculateOrderTotal)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    public List<OrderSummaryDto> getRecentOrdersWithDetails(int days) {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(days);
        List<Order> recentOrders = orderRepository.findByOrderDateAfter(cutoffDate);
        
        return recentOrders.stream()
                .map(this::createDetailedOrderSummary)
                .collect(Collectors.toList());
    }

    public int getTotalItemsCount() {
        List<Order> orders = orderRepository.findAll();
        return orders.stream()
                .mapToInt(order -> order.getItems().size())
                .sum();
    }

    private OrderSummaryDto createOrderSummary(Order order) {
        OrderSummaryDto summary = new OrderSummaryDto();
        summary.setOrderId(order.getId());
        summary.setCustomerName(order.getCustomerName());
        summary.setOrderDate(order.getOrderDate());
        summary.setItemCount(order.getItems().size());
        summary.setTotalAmount(calculateOrderTotal(order));
        return summary;
    }

    private OrderSummaryDto createDetailedOrderSummary(Order order) {
        OrderSummaryDto summary = createOrderSummary(order);
        summary.setItemDetails(extractItemDetails(order));
        summary.setAverageItemPrice(calculateAverageItemPrice(order));
        return summary;
    }

    private BigDecimal calculateOrderTotal(Order order) {
        return order.getItems().stream()
                .map(item -> item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private List<String> extractItemDetails(Order order) {
        return order.getItems().stream()
                .map(item -> String.format("%s (Qty: %d, Price: %s)", 
                    item.getProductName(), item.getQuantity(), item.getPrice()))
                .collect(Collectors.toList());
    }

    private BigDecimal calculateAverageItemPrice(Order order) {
        List<OrderItem> items = order.getItems();
        if (items.isEmpty()) {
            return BigDecimal.ZERO;
        }
        
        BigDecimal totalPrice = items.stream()
                .map(OrderItem::getPrice)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
        
        return totalPrice.divide(BigDecimal.valueOf(items.size()));
    }

    @Transactional(readOnly = true)
    public boolean hasHighValueOrders(BigDecimal threshold) {
        List<Order> orders = orderRepository.findAll();
        return orders.stream()
                .anyMatch(order -> calculateOrderTotal(order).compareTo(threshold) > 0);
    }

    public List<String> getTopCustomersByOrderValue(int limit) {
        List<Order> orders = orderRepository.findAll();
        return orders.stream()
                .collect(Collectors.groupingBy(Order::getCustomerName,
                    Collectors.reducing(BigDecimal.ZERO, this::calculateOrderTotal, BigDecimal::add)))
                .entrySet().stream()
                .sorted((e1, e2) -> e2.getValue().compareTo(e1.getValue()))
                .limit(limit)
                .map(entry -> String.format("%s: %s", entry.getKey(), entry.getValue()))
                .collect(Collectors.toList());
    }
}