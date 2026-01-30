# User Profile Caching

## Overview

The user profile service needs caching to reduce database load. User profiles are frequently accessed and rarely change, making them good candidates for caching.

## Requirements

1. Cache user profile data to reduce database queries
2. Support cache invalidation on profile update
3. Different users must see their own profile data
4. Cache expiration after 1 hour
5. Support millions of concurrent users

## Constraints

1. Each user must only see their own data
2. Cache must be thread-safe
3. Memory usage must be bounded
4. Stale data must be refreshed on profile update

## References

See context.md for existing caching configuration.
