# Django Cache Warming System for Production Deployments

## Overview

The system needs to implement an automated cache warming mechanism that pre-populates critical application caches immediately after deployment to production environments. This ensures optimal performance from the moment the application goes live by eliminating cold cache penalties for initial user requests. The cache warming should target frequently accessed data such as user sessions, database query results, and computed values that are expensive to generate.

## Requirements

1. Create a Django management command that can be executed during deployment pipeline to warm application caches
2. Implement cache warming for user authentication data including active user sessions and permission mappings
3. Pre-populate database query caches for frequently accessed models such as user profiles, application settings, and reference data
4. Warm template fragment caches for commonly rendered page components and navigation elements
5. Include cache warming for computed values like aggregated statistics, report data, and dashboard metrics
6. Provide configurable cache warming strategies that can be adjusted based on application usage patterns
7. Implement progress tracking and logging to monitor cache warming completion status
8. Support selective cache warming where specific cache keys or categories can be targeted
9. Include error handling and retry mechanisms for failed cache warming operations
10. Ensure cache warming operations are idempotent and safe to run multiple times
11. Implement cache validation to verify that warmed data is correctly stored and accessible
12. Support both synchronous and asynchronous cache warming execution modes

## Constraints

1. Cache warming operations must not interfere with live application traffic or cause performance degradation
2. The system must handle cases where cache backends are temporarily unavailable or experiencing high load
3. Cache warming must respect existing cache TTL settings and not override configured expiration times
4. Memory usage during cache warming operations must be bounded to prevent system resource exhaustion
5. Cache warming should gracefully handle scenarios where source data for warming is unavailable or corrupted
6. The implementation must be compatible with multiple cache backend types including Redis, Memcached, and database caching
7. Cache warming operations must complete within reasonable time limits to avoid blocking deployment processes

## References

See context.md for existing cache configuration, model definitions, and current caching patterns used throughout the application.