package com.example.ecommerce.service;

import com.example.ecommerce.entity.OrderItem;
import com.example.ecommerce.repository.OrderItemRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class SalesAnalyticsService {

    @Autowired
    private OrderItemRepository orderItemRepository;

    @Transactional(readOnly = true)
    public Map<Long, Long> getRevenueByCategory() {
        List<OrderItem> allItems = orderItemRepository.findAll();

        return allItems.stream()
                .collect(Collectors.groupingBy(
                        item -> item.getProduct().getCategory().getId(),
                        Collectors.summingLong(item -> (long) item.getPriceCents() * item.getQuantity())
                ));
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> getTopSellingProducts(int limit) {
        List<OrderItem> allItems = orderItemRepository.findAll();

        Map<Long, Long> productQuantities = allItems.stream()
                .collect(Collectors.groupingBy(
                        item -> item.getProduct().getId(),
                        Collectors.summingLong(OrderItem::getQuantity)
                ));

        return productQuantities.entrySet().stream()
                .sorted(Map.Entry.<Long, Long>comparingByValue().reversed())
                .limit(limit)
                .map(entry -> {
                    Map<String, Object> result = new HashMap<>();
                    result.put("productId", entry.getKey());
                    result.put("totalQuantity", entry.getValue());
                    return result;
                })
                .collect(Collectors.toList());
    }

    @Transactional(readOnly = true)
    public Map<String, Long> getMonthlySalesTrend(int year) {
        List<OrderItem> allItems = orderItemRepository.findAll();

        return allItems.stream()
                .filter(item -> item.getCreatedAt().getYear() == year)
                .collect(Collectors.groupingBy(
                        item -> String.format("%d-%02d", year, item.getCreatedAt().getMonthValue()),
                        TreeMap::new,
                        Collectors.summingLong(item -> (long) item.getPriceCents() * item.getQuantity())
                ));
    }

    @Transactional(readOnly = true)
    public Map<String, Object> getSalesAnalytics(LocalDateTime startDate, LocalDateTime endDate) {
        List<OrderItem> items = orderItemRepository.findByCreatedAtBetween(startDate, endDate);

        long totalRevenue = items.stream()
                .mapToLong(item -> (long) item.getPriceCents() * item.getQuantity())
                .sum();

        long totalQuantity = items.stream()
                .mapToLong(OrderItem::getQuantity)
                .sum();

        double averageOrderValue = items.isEmpty() ? 0 :
                (double) totalRevenue / items.stream()
                        .map(item -> item.getOrder().getId())
                        .distinct()
                        .count();

        Map<String, Object> analytics = new HashMap<>();
        analytics.put("totalRevenue", totalRevenue);
        analytics.put("totalQuantity", totalQuantity);
        analytics.put("averageOrderValue", averageOrderValue);
        analytics.put("itemCount", items.size());

        return analytics;
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> getProductPerformanceReport() {
        List<OrderItem> allItems = orderItemRepository.findAll();

        Map<Long, DoubleSummaryStatistics> productStats = allItems.stream()
                .collect(Collectors.groupingBy(
                        item -> item.getProduct().getId(),
                        Collectors.summarizingDouble(item -> item.getPriceCents() * item.getQuantity())
                ));

        return productStats.entrySet().stream()
                .sorted((e1, e2) -> Double.compare(e2.getValue().getSum(), e1.getValue().getSum()))
                .map(entry -> {
                    Map<String, Object> report = new HashMap<>();
                    report.put("productId", entry.getKey());
                    report.put("totalRevenue", entry.getValue().getSum());
                    report.put("orderCount", entry.getValue().getCount());
                    report.put("averageRevenue", entry.getValue().getAverage());
                    return report;
                })
                .collect(Collectors.toList());
    }
}
