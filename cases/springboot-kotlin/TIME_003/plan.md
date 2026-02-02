# Campaign Period Validation Service

## Overview

The system needs to validate whether a campaign is currently active based on its configured time period. This validation is critical for ensuring that campaign discounts and promotions are only applied during their intended timeframe. The service must handle various time-related scenarios including timezone considerations, boundary conditions, and different date formats.

## Requirements

1. The service must validate if the current timestamp falls within a campaign's start and end date range
2. Campaign start and end dates must be inclusive (valid on both boundary dates)
3. The service must handle timezone-aware date comparisons using the system's default timezone
4. Campaign validation must return a boolean result indicating active status
5. The service must accept campaign objects containing start date, end date, and campaign identifier
6. Date validation must work with LocalDateTime objects for precise time comparison
7. The service must be implemented as a Spring Boot service component with proper dependency injection
8. Campaign period validation must be performed before any discount calculations
9. The service must handle null or missing date values gracefully
10. Validation results must be logged for audit purposes

## Constraints

1. Campaign start date cannot be after the campaign end date
2. Both start and end dates are required fields and cannot be null
3. Past campaigns (end date before current time) must be marked as inactive
4. Future campaigns (start date after current time) must be marked as inactive
5. The service must not modify campaign data during validation
6. Time comparisons must account for millisecond precision
7. The validation must complete within reasonable performance bounds for high-traffic scenarios

## References

See context.md for existing campaign management implementations and related service patterns used in the codebase.