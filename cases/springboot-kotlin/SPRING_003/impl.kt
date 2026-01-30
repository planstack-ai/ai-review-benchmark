package com.example.benchmark.service

import com.example.benchmark.dto.ReviewRequest
import com.example.benchmark.dto.ReviewResponse
import com.example.benchmark.entity.CodeReview
import com.example.benchmark.entity.ReviewMetrics
import com.example.benchmark.exception.ReviewProcessingException
import com.example.benchmark.repository.CodeReviewRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.List
import java.util.Optional
import java.util.UUID

@Service
@Transactional
class CodeReviewBenchmarkService {

    @Autowired
    private OrderService orderService

    @Autowired
    private CodeReviewRepository codeReviewRepository

    @Autowired
    private MetricsCalculationService metricsService

    @Autowired
    private NotificationService notificationService

    fun processCodeReview(request: ReviewRequest): ReviewResponse {
        validateReviewRequest(request)
        
        CodeReview review = createCodeReview(request)
        ReviewMetrics metrics = calculateReviewMetrics(review)
        
        review.setMetrics(metrics)
        review.setStatus("COMPLETED")
        review.setCompletedAt(LocalDateTime.now())
        
        CodeReview savedReview = codeReviewRepository.save(review)
        
        if (shouldCreateOrder(metrics)) {
            createPremiumOrder(savedReview)
        }
        
        notifyReviewCompletion(savedReview)
        
        return buildReviewResponse(savedReview)
    }

    fun List<ReviewResponse> getBenchmarkResults(userId: String) {
        List<CodeReview> reviews = codeReviewRepository.findByUserIdOrderByCreatedAtDesc(userId)
        return reviews.stream()
                .map(this::buildReviewResponse)
                .toList()
    }

    fun Optional<ReviewResponse> getReviewById(reviewId: UUID) {
        return codeReviewRepository.findById(reviewId)
                .map(this::buildReviewResponse)
    }

    private fun validateReviewRequest(request: ReviewRequest): {
        if (request.CodeSnippet == null || request.CodeSnippet.trim().isEmpty()) {
            throw new ReviewProcessingException("Code snippet cannot be empty")
        }
        if (request.UserId == null) {
            throw new ReviewProcessingException("User ID is required")
        }
    }

    private fun createCodeReview(request: ReviewRequest): CodeReview {
        CodeReview review = new CodeReview()
        review.setId(UUID.randomUUID())
        review.setUserId(request.UserId)
        review.setCodeSnippet(request.CodeSnippet)
        review.setLanguage(request.Language)
        review.setStatus("PROCESSING")
        review.setCreatedAt(LocalDateTime.now())
        return review
    }

    private fun calculateReviewMetrics(review: CodeReview): ReviewMetrics {
        return metricsService.analyzeCode(
            review.CodeSnippet,
            review.Language
        )
    }

    private fun shouldCreateOrder(metrics: ReviewMetrics): boolean {
        return metrics.ComplexityScore.compareTo(BigDecimal("8.0")) > 0 ||
               metrics.BugCount > 5
    }

    private fun createPremiumOrder(review: CodeReview): {
        BigDecimal orderAmount = calculateOrderAmount(review.Metrics)
        orderService.createPremiumAnalysisOrder(
            review.UserId,
            review.Id,
            orderAmount
        )
    }

    private fun calculateOrderAmount(metrics: ReviewMetrics): BigDecimal {
        BigDecimal baseAmount = BigDecimal("29.99")
        BigDecimal complexityMultiplier = metrics.ComplexityScore
                .divide(BigDecimal("10.0"), 2, BigDecimal.ROUND_HALF_UP)
        return baseAmount.multiply(complexityMultiplier)
    }

    private fun notifyReviewCompletion(review: CodeReview): {
        notificationService.sendReviewCompletionNotification(
            review.UserId,
            review.Id,
            review.Metrics.getOverallScore()
        )
    }

    private fun buildReviewResponse(review: CodeReview): ReviewResponse {
        ReviewResponse response = new ReviewResponse()
        response.setReviewId(review.Id)
        response.setUserId(review.UserId)
        response.setStatus(review.Status)
        response.setCreatedAt(review.CreatedAt)
        response.setCompletedAt(review.CompletedAt)
        
        if (review.Metrics != null) {
            response.setComplexityScore(review.Metrics.getComplexityScore())
            response.setBugCount(review.Metrics.getBugCount())
            response.setOverallScore(review.Metrics.getOverallScore())
            response.setRecommendations(review.Metrics.getRecommendations())
        }
        
        return response
    }
}