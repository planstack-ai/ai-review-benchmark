# Code Review Benchmark Service

## Overview

This service processes code review requests and calculates quality metrics for an AI code review benchmark platform. The service handles review processing, metrics calculation, and optional premium order creation for complex code analysis.

## Requirements

1. Create a service class that processes code review requests
2. The service must integrate with OrderService, CodeReviewRepository, MetricsCalculationService, and NotificationService
3. Implement a method to process code reviews that validates input, calculates metrics, and saves results
4. Implement a method to retrieve benchmark results for a specific user
5. Implement a method to get a single review by ID
6. The service should create premium analysis orders when code complexity exceeds thresholds
7. Send notifications when reviews are completed
8. Use proper Spring dependency injection patterns following best practices

## Constraints

1. Code snippets cannot be empty or null
2. User ID is required for all review requests
3. Premium orders should be created when complexity score > 8.0 or bug count > 5
4. All monetary calculations must use BigDecimal for precision
5. The service must be transactional
6. Follow Spring Boot best practices for dependency injection and testability

## References

See context.md for existing entity definitions and related Spring Boot configuration details.