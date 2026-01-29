package com.example.ecommerce.service;

import com.example.ecommerce.entity.Order;
import com.example.ecommerce.entity.Product;
import com.example.ecommerce.entity.User;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.ProductRepository;
import com.example.ecommerce.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class DashboardStatisticsService {

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private ProductRepository productRepository;

    @Transactional(readOnly = true)
    public Map<String, Object> getDashboardStatistics() {
        Map<String, Object> stats = new HashMap<>();

        stats.put("totalOrders", getTotalOrderCount());
        stats.put("ordersByStatus", getOrderCountsByStatus());
        stats.put("totalUsers", getTotalUserCount());
        stats.put("activeUsers", getActiveUserCount());
        stats.put("totalProducts", getTotalProductCount());

        return stats;
    }

    private int getTotalOrderCount() {
        List<Order> orders = orderRepository.findAll();
        return orders.size();
    }

    private Map<String, Integer> getOrderCountsByStatus() {
        Map<String, Integer> statusCounts = new HashMap<>();

        List<Order> pendingOrders = orderRepository.findByStatus("pending");
        statusCounts.put("pending", pendingOrders.size());

        List<Order> completedOrders = orderRepository.findByStatus("completed");
        statusCounts.put("completed", completedOrders.size());

        List<Order> cancelledOrders = orderRepository.findByStatus("cancelled");
        statusCounts.put("cancelled", cancelledOrders.size());

        List<Order> shippedOrders = orderRepository.findByStatus("shipped");
        statusCounts.put("shipped", shippedOrders.size());

        return statusCounts;
    }

    private int getTotalUserCount() {
        List<User> users = userRepository.findAll();
        return users.size();
    }

    private int getActiveUserCount() {
        List<User> activeUsers = userRepository.findByActiveTrue();
        return activeUsers.size();
    }

    private int getTotalProductCount() {
        List<Product> products = productRepository.findAll();
        return products.size();
    }

    @Transactional(readOnly = true)
    public Map<String, Integer> getProductCountsByCategory(List<Long> categoryIds) {
        Map<String, Integer> categoryCounts = new HashMap<>();

        for (Long categoryId : categoryIds) {
            List<Product> products = productRepository.findByCategoryId(categoryId);
            categoryCounts.put("category_" + categoryId, products.size());
        }

        return categoryCounts;
    }
}
