# User-Specific Cache Key Implementation

## Overview

The application needs to implement a caching mechanism that ensures data isolation between different users. This is critical for maintaining data privacy and security, as cached data should never be shared between users or accessed by unauthorized parties. The system must generate unique cache keys that incorporate user identification to prevent cache collisions and data leakage.

## Requirements

1. All cache keys must include the user identifier as part of the key structure
2. Cache keys must be unique per user to prevent data sharing between different users
3. The cache key format must be consistent across all caching operations
4. Cache operations (read, write, delete) must use the same user-specific key generation logic
5. The system must handle cases where user context is available for cache key generation
6. Cache keys must be deterministic - the same user and operation should always generate the same key
7. The implementation must prevent cache key collisions between different users accessing the same resource

## Constraints

1. User identifier must be validated and present before generating cache keys
2. Cache keys should not expose sensitive user information in plain text
3. The system must gracefully handle missing or invalid user context
4. Cache key length should remain within reasonable limits for the caching backend
5. The implementation must be thread-safe for concurrent user operations

## References

See context.md for existing caching patterns and user authentication mechanisms in the codebase.