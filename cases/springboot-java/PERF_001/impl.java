package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.OrderItem;
import com.example.ecommerce.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class OrderReportService {

    @Autowired
    private OrderRepository orderRepository;

    private LocalDateTime startDate;
    private LocalDateTime endDate;

    public OrderReportService() {
        this.endDate = LocalDateTime.now();
        this.startDate = endDate.minusDays(30);
    }

    public void setDateRange(LocalDateTime start, LocalDateTime end) {
        this.startDate = start;
        this.endDate = end;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> generateSummaryReport() {
        List<Order> orders = fetchOrders();
        if (orders.isEmpty()) {
            return emptyReport();
        }

        Map<String, Object> report = new HashMap<>();
        report.put("totalOrders", orders.size());
        report.put("totalRevenue", calculateTotalRevenue(orders));
        report.put("productBreakdown", generateProductBreakdown(orders));
        report.put("averageOrderValue", calculateAverageOrderValue(orders));
        report.put("topProducts", identifyTopProducts(orders));
        return report;
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> exportDetailedReport() {
        List<Order> orders = fetchOrdersWithDetails();
        List<Map<String, Object>> reportData = new ArrayList<>();

        for (Order order : orders) {
            Map<String, Object> orderSummary = buildOrderSummary(order);
            reportData.add(orderSummary);
        }

        return reportData;
    }

    private List<Order> fetchOrders() {
        return orderRepository.findByCreatedAtBetween(startDate, endDate);
    }

    private List<Order> fetchOrdersWithDetails() {
        return orderRepository.findByCreatedAtBetween(startDate, endDate);
    }

    private Map<String, Object> buildOrderSummary(Order order) {
        List<Map<String, Object>> itemDetails = collectItemDetails(order);

        Map<String, Object> summary = new HashMap<>();
        summary.put("orderId", order.getId());
        summary.put("orderDate", order.getCreatedAt());
        summary.put("totalAmount", order.getTotalCents());
        summary.put("itemsCount", order.getItems().size());
        summary.put("itemDetails", itemDetails);
        return summary;
    }

    private List<Map<String, Object>> collectItemDetails(Order order) {
        List<Map<String, Object>> details = new ArrayList<>();

        order.getItems().forEach(item -> {
            Map<String, Object> itemDetail = new HashMap<>();
            itemDetail.put("productName", item.getProduct().getName());
            itemDetail.put("quantity", item.getQuantity());
            itemDetail.put("unitPrice", item.getPriceCents());
            itemDetail.put("totalPrice", item.getPriceCents() * item.getQuantity());
            details.add(itemDetail);
        });

        return details;
    }

    private long calculateTotalRevenue(List<Order> orders) {
        return orders.stream()
                .mapToLong(Order::getTotalCents)
                .sum();
    }

    private double calculateAverageOrderValue(List<Order> orders) {
        if (orders.isEmpty()) {
            return 0;
        }
        return (double) calculateTotalRevenue(orders) / orders.size();
    }

    private Map<String, Long> generateProductBreakdown(List<Order> orders) {
        Map<String, Long> productSales = new HashMap<>();

        for (Order order : orders) {
            for (OrderItem item : order.getItems()) {
                String productName = item.getProduct().getName();
                long itemTotal = (long) item.getPriceCents() * item.getQuantity();
                productSales.merge(productName, itemTotal, Long::sum);
            }
        }

        return productSales;
    }

    private Map<String, Long> identifyTopProducts(List<Order> orders) {
        Map<String, Long> breakdown = generateProductBreakdown(orders);
        Map<String, Long> topProducts = new HashMap<>();

        breakdown.entrySet().stream()
                .sorted(Map.Entry.<String, Long>comparingByValue().reversed())
                .limit(5)
                .forEach(e -> topProducts.put(e.getKey(), e.getValue()));

        return topProducts;
    }

    private Map<String, Object> emptyReport() {
        Map<String, Object> report = new HashMap<>();
        report.put("totalOrders", 0);
        report.put("totalRevenue", 0L);
        report.put("productBreakdown", new HashMap<>());
        report.put("averageOrderValue", 0.0);
        report.put("topProducts", new HashMap<>());
        return report;
    }
}
