package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.YearMonth;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class SalesReportService {

    @Autowired
    private OrderRepository orderRepository;

    @Transactional(readOnly = true)
    public Map<String, Object> generateMonthlySalesReport(YearMonth month) {
        LocalDateTime startOfMonth = month.atDay(1).atStartOfDay();
        LocalDateTime endOfMonth = month.atEndOfMonth().atTime(23, 59, 59);

        List<Order> allOrders = orderRepository.findAll();

        List<Order> monthlyOrders = allOrders.stream()
                .filter(order -> !order.getCreatedAt().isBefore(startOfMonth)
                        && !order.getCreatedAt().isAfter(endOfMonth))
                .collect(Collectors.toList());

        Map<String, Object> report = new HashMap<>();
        report.put("month", month.toString());
        report.put("totalOrders", monthlyOrders.size());
        report.put("totalRevenue", calculateTotalRevenue(monthlyOrders));
        report.put("ordersByStatus", countOrdersByStatus(monthlyOrders));
        report.put("averageOrderValue", calculateAverageOrderValue(monthlyOrders));

        return report;
    }

    @Transactional(readOnly = true)
    public Map<String, Object> generateYearlySalesReport(int year) {
        List<Order> allOrders = orderRepository.findAll();

        List<Order> yearlyOrders = allOrders.stream()
                .filter(order -> order.getCreatedAt().getYear() == year)
                .collect(Collectors.toList());

        Map<String, Object> report = new HashMap<>();
        report.put("year", year);
        report.put("totalOrders", yearlyOrders.size());
        report.put("totalRevenue", calculateTotalRevenue(yearlyOrders));
        report.put("monthlyBreakdown", generateMonthlyBreakdown(yearlyOrders));

        return report;
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> exportAllOrdersForAudit() {
        List<Order> allOrders = orderRepository.findAll();

        return allOrders.stream()
                .map(this::orderToMap)
                .collect(Collectors.toList());
    }

    private long calculateTotalRevenue(List<Order> orders) {
        return orders.stream()
                .mapToLong(Order::getTotalCents)
                .sum();
    }

    private Map<String, Long> countOrdersByStatus(List<Order> orders) {
        return orders.stream()
                .collect(Collectors.groupingBy(Order::getStatus, Collectors.counting()));
    }

    private double calculateAverageOrderValue(List<Order> orders) {
        if (orders.isEmpty()) {
            return 0.0;
        }
        return (double) calculateTotalRevenue(orders) / orders.size();
    }

    private Map<Integer, Long> generateMonthlyBreakdown(List<Order> orders) {
        return orders.stream()
                .collect(Collectors.groupingBy(
                        order -> order.getCreatedAt().getMonthValue(),
                        Collectors.summingLong(Order::getTotalCents)
                ));
    }

    private Map<String, Object> orderToMap(Order order) {
        Map<String, Object> map = new HashMap<>();
        map.put("id", order.getId());
        map.put("userId", order.getUserId());
        map.put("totalCents", order.getTotalCents());
        map.put("status", order.getStatus());
        map.put("createdAt", order.getCreatedAt());
        return map;
    }
}
