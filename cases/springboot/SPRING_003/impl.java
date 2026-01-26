package com.example.benchmark.service;

import com.example.benchmark.dto.ReviewRequest;
import com.example.benchmark.dto.ReviewResponse;
import com.example.benchmark.entity.CodeReview;
import com.example.benchmark.entity.ReviewMetrics;
import com.example.benchmark.exception.ReviewProcessingException;
import com.example.benchmark.repository.CodeReviewRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@Transactional
public class CodeReviewBenchmarkService {

    @Autowired
    private OrderService orderService;

    @Autowired
    private CodeReviewRepository codeReviewRepository;

    @Autowired
    private MetricsCalculationService metricsService;

    @Autowired
    private NotificationService notificationService;

    public ReviewResponse processCodeReview(ReviewRequest request) {
        validateReviewRequest(request);
        
        CodeReview review = createCodeReview(request);
        ReviewMetrics metrics = calculateReviewMetrics(review);
        
        review.setMetrics(metrics);
        review.setStatus("COMPLETED");
        review.setCompletedAt(LocalDateTime.now());
        
        CodeReview savedReview = codeReviewRepository.save(review);
        
        if (shouldCreateOrder(metrics)) {
            createPremiumOrder(savedReview);
        }
        
        notifyReviewCompletion(savedReview);
        
        return buildReviewResponse(savedReview);
    }

    public List<ReviewResponse> getBenchmarkResults(String userId) {
        List<CodeReview> reviews = codeReviewRepository.findByUserIdOrderByCreatedAtDesc(userId);
        return reviews.stream()
                .map(this::buildReviewResponse)
                .toList();
    }

    public Optional<ReviewResponse> getReviewById(UUID reviewId) {
        return codeReviewRepository.findById(reviewId)
                .map(this::buildReviewResponse);
    }

    private void validateReviewRequest(ReviewRequest request) {
        if (request.getCodeSnippet() == null || request.getCodeSnippet().trim().isEmpty()) {
            throw new ReviewProcessingException("Code snippet cannot be empty");
        }
        if (request.getUserId() == null) {
            throw new ReviewProcessingException("User ID is required");
        }
    }

    private CodeReview createCodeReview(ReviewRequest request) {
        CodeReview review = new CodeReview();
        review.setId(UUID.randomUUID());
        review.setUserId(request.getUserId());
        review.setCodeSnippet(request.getCodeSnippet());
        review.setLanguage(request.getLanguage());
        review.setStatus("PROCESSING");
        review.setCreatedAt(LocalDateTime.now());
        return review;
    }

    private ReviewMetrics calculateReviewMetrics(CodeReview review) {
        return metricsService.analyzeCode(
            review.getCodeSnippet(),
            review.getLanguage()
        );
    }

    private boolean shouldCreateOrder(ReviewMetrics metrics) {
        return metrics.getComplexityScore().compareTo(BigDecimal.valueOf(8.0)) > 0 ||
               metrics.getBugCount() > 5;
    }

    private void createPremiumOrder(CodeReview review) {
        BigDecimal orderAmount = calculateOrderAmount(review.getMetrics());
        orderService.createPremiumAnalysisOrder(
            review.getUserId(),
            review.getId(),
            orderAmount
        );
    }

    private BigDecimal calculateOrderAmount(ReviewMetrics metrics) {
        BigDecimal baseAmount = BigDecimal.valueOf(29.99);
        BigDecimal complexityMultiplier = metrics.getComplexityScore()
                .divide(BigDecimal.valueOf(10.0), 2, BigDecimal.ROUND_HALF_UP);
        return baseAmount.multiply(complexityMultiplier);
    }

    private void notifyReviewCompletion(CodeReview review) {
        notificationService.sendReviewCompletionNotification(
            review.getUserId(),
            review.getId(),
            review.getMetrics().getOverallScore()
        );
    }

    private ReviewResponse buildReviewResponse(CodeReview review) {
        ReviewResponse response = new ReviewResponse();
        response.setReviewId(review.getId());
        response.setUserId(review.getUserId());
        response.setStatus(review.getStatus());
        response.setCreatedAt(review.getCreatedAt());
        response.setCompletedAt(review.getCompletedAt());
        
        if (review.getMetrics() != null) {
            response.setComplexityScore(review.getMetrics().getComplexityScore());
            response.setBugCount(review.getMetrics().getBugCount());
            response.setOverallScore(review.getMetrics().getOverallScore());
            response.setRecommendations(review.getMetrics().getRecommendations());
        }
        
        return response;
    }
}