package com.example.ecommerce.service;

import com.example.ecommerce.entity.User;
import com.example.ecommerce.repository.OrderRepository;
import com.example.ecommerce.repository.UserRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class UserMetricsBatchService {

    private static final Logger logger = LoggerFactory.getLogger(UserMetricsBatchService.class);

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private OrderRepository orderRepository;

    @Scheduled(cron = "0 0 2 * * *")
    @Transactional
    public Map<String, Object> updateAllUserMetrics() {
        logger.info("Starting bulk user metrics update");

        List<User> activeUsers = userRepository.findByActiveTrue();
        int processed = 0;
        int failed = 0;

        for (User user : activeUsers) {
            try {
                updateUserMetrics(user.getId());
                processed++;
            } catch (Exception e) {
                logger.error("Failed to update metrics for user: " + user.getId(), e);
                failed++;
            }
        }

        Map<String, Object> result = new HashMap<>();
        result.put("totalUsers", activeUsers.size());
        result.put("processed", processed);
        result.put("failed", failed);

        logger.info("Completed bulk user metrics update: {}", result);
        return result;
    }

    @Transactional
    public void updateUserMetrics(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("User not found: " + userId));

        long orderCount = orderRepository.countByUserId(userId);

        int engagementScore = calculateEngagementScore(orderCount, user.getLastActive());

        user.setOrderCount((int) orderCount);
        user.setEngagementScore(engagementScore);

        userRepository.save(user);
    }

    @Transactional
    public void recalculateAllEngagementScores() {
        List<User> allUsers = userRepository.findByActiveTrue();

        for (User user : allUsers) {
            long orderCount = orderRepository.countByUserId(user.getId());
            int score = calculateEngagementScore(orderCount, user.getLastActive());

            userRepository.updateEngagementScore(user.getId(), score);
        }
    }

    @Transactional
    public Map<String, Object> generateUserActivityReport() {
        List<User> users = userRepository.findByActiveTrue();
        Map<String, Object> report = new HashMap<>();

        int highEngagement = 0;
        int mediumEngagement = 0;
        int lowEngagement = 0;
        long totalOrders = 0;

        for (User user : users) {
            long orderCount = orderRepository.countByUserId(user.getId());
            totalOrders += orderCount;

            int score = calculateEngagementScore(orderCount, user.getLastActive());
            if (score >= 80) {
                highEngagement++;
            } else if (score >= 50) {
                mediumEngagement++;
            } else {
                lowEngagement++;
            }
        }

        report.put("totalUsers", users.size());
        report.put("totalOrders", totalOrders);
        report.put("highEngagement", highEngagement);
        report.put("mediumEngagement", mediumEngagement);
        report.put("lowEngagement", lowEngagement);
        report.put("averageOrdersPerUser", users.isEmpty() ? 0 : (double) totalOrders / users.size());

        return report;
    }

    private int calculateEngagementScore(long orderCount, LocalDateTime lastActive) {
        int score = 0;

        if (orderCount >= 10) {
            score += 50;
        } else if (orderCount >= 5) {
            score += 30;
        } else if (orderCount >= 1) {
            score += 10;
        }

        if (lastActive != null) {
            long daysSinceActive = java.time.temporal.ChronoUnit.DAYS.between(lastActive, LocalDateTime.now());
            if (daysSinceActive <= 7) {
                score += 50;
            } else if (daysSinceActive <= 30) {
                score += 30;
            } else if (daysSinceActive <= 90) {
                score += 10;
            }
        }

        return Math.min(score, 100);
    }
}
