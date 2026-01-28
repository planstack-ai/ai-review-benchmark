# User Profile Query Optimization

## Overview

The system needs to efficiently retrieve user profiles based on various search criteria. Users frequently search for profiles by email address, username, and registration date ranges. The application serves thousands of concurrent users, making query performance critical for maintaining responsive user experience and system scalability.

## Requirements

1. Create a User model with fields for username, email, first_name, last_name, and date_joined
2. Implement database indexes on frequently queried fields (email and username)
3. Create a UserProfile model linked to User with additional fields including bio, location, and is_verified status
4. Implement database indexes on UserProfile fields that are commonly used in filtering operations
5. Provide a search functionality that allows filtering users by email address with case-insensitive matching
6. Implement username-based user lookup functionality for authentication and profile retrieval
7. Create date range filtering capability for finding users who registered within specific time periods
8. Ensure all search and filter operations utilize the appropriate database indexes for optimal performance
9. Implement proper foreign key relationships between User and UserProfile models
10. Create Django model managers or QuerySet methods to encapsulate common query patterns

## Constraints

1. Email addresses must be unique across all users
2. Usernames must be unique and contain only alphanumeric characters and underscores
3. Date range queries must handle both start and end date parameters, with either being optional
4. Case-insensitive email searches must maintain consistent behavior across different database backends
5. All database queries must be optimized to avoid N+1 query problems when accessing related UserProfile data
6. The system must handle large datasets efficiently (assume 100,000+ user records)

## References

See context.md for existing database schema patterns and Django model implementation examples used in the current codebase.