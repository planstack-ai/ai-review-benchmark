# User-Specific Cache Key Design for Django Application

## Overview

The application needs to implement a caching mechanism that stores user-specific data to improve performance and reduce database queries. The cache system must ensure that each user's data is properly isolated and that cache keys are designed to prevent data leakage between different users. This is critical for maintaining data privacy and security in a multi-user environment.

## Requirements

1. All cache keys must include the user ID as a component to ensure user-specific isolation
2. Cache keys must follow a consistent naming convention that clearly identifies the cached content type
3. The cache implementation must handle both authenticated and anonymous users appropriately
4. Cache keys must be unique across different data types for the same user
5. The system must provide a mechanism to invalidate user-specific cache entries when user data changes
6. Cache operations must gracefully handle cases where user information is not available
7. All cached data must be associated with the correct user context to prevent cross-user data exposure
8. The cache key generation must be deterministic for the same user and data type combination

## Constraints

1. Anonymous users must not share cache entries with authenticated users
2. Cache keys must not exceed the maximum length supported by the caching backend
3. User IDs must be validated before being used in cache key generation
4. The system must handle user session changes without serving stale cached data
5. Cache invalidation must be atomic to prevent partial data inconsistencies

## References

See context.md for existing cache implementations and patterns used in the codebase.