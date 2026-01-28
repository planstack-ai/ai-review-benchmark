# Asynchronous Order Processing Without @EnableAsync

## Overview

The system needs to process customer orders asynchronously to improve response times and user experience. When a customer places an order, the system should immediately return a confirmation while processing the order details (inventory checks, payment processing, shipping calculations) in the background. This ensures the web interface remains responsive even during high-traffic periods.

## Requirements

1. Create an OrderController that accepts order requests via REST API
2. Implement an OrderService that processes orders asynchronously using Spring's @Async annotation
3. The order processing should include inventory validation, payment processing, and shipping calculation steps
4. Return an immediate response to the client with order confirmation details
5. Log the start and completion of asynchronous order processing operations
6. Handle order processing failures gracefully with appropriate error logging
7. Ensure proper thread separation between the web request thread and background processing thread
8. Configure appropriate thread pool settings for asynchronous execution
9. Implement proper exception handling for async operations that don't propagate to the caller

## Constraints

1. Orders must have valid customer information (non-null customer ID and email)
2. Order total must be greater than zero
3. Inventory checks should simulate realistic processing time (minimum 1 second delay)
4. Payment processing should simulate network calls with appropriate delays
5. The system should handle concurrent order processing efficiently
6. Async methods must be called from different classes to ensure proxy-based AOP works correctly
7. Thread pool should be properly configured to prevent resource exhaustion

## References

See context.md for examples of existing Spring Boot async implementations and configuration patterns.