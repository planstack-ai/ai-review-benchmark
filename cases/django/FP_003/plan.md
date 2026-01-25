# User Activity Tracking System

## Overview

The system needs to track user activities within a web application, providing administrators with insights into user behavior patterns. The system should maintain a log of user actions with timestamps and allow for efficient querying of activity data for reporting and analytics purposes.

## Requirements

1. Create a UserActivity model that stores user actions with appropriate fields for tracking
2. Implement a method to record new user activities with automatic timestamp generation
3. Provide functionality to retrieve activities for a specific user within a date range
4. Create a method to get the most recent activities across all users with pagination support
5. Implement filtering capabilities to search activities by action type
6. Provide a count method to get total activities for statistical reporting
7. Create a method to retrieve activities from the last N days for dashboard display
8. Implement bulk activity recording for batch operations
9. Provide a method to get unique action types for filter dropdown population
10. Create functionality to retrieve activities grouped by date for trend analysis

## Constraints

1. All database queries must use Django ORM QuerySet operations
2. Date filtering should handle timezone-aware datetime objects
3. Pagination should be implemented using Django's standard pagination mechanisms
4. Activity records should be immutable once created (no update operations)
5. All methods should handle empty result sets gracefully
6. Query performance should be optimized for large datasets
7. User references must maintain referential integrity
8. Date range queries should be inclusive of start and end dates

## References

See context.md for existing model definitions and database schema requirements.