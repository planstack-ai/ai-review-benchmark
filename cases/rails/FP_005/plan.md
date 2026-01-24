# User Profile Management with Standard Callbacks

## Overview

The system needs to manage user profiles with automatic data processing when users are created, updated, or deleted. This includes generating welcome emails, updating search indexes, and cleaning up associated data. The implementation should use Rails' standard callback mechanisms to ensure data consistency and proper business logic execution.

## Requirements

1. User model must automatically send a welcome email when a new user is created
2. User profile search index must be updated whenever user data changes
3. User's associated data (sessions, preferences, etc.) must be cleaned up when a user is deleted
4. Email notifications must be sent to administrators when user accounts are deactivated
5. User activity timestamps must be automatically maintained for audit purposes
6. Profile completion status must be recalculated whenever profile fields are updated
7. User statistics cache must be invalidated when relevant user data changes
8. System must log all user lifecycle events for compliance tracking

## Constraints

1. Callbacks must not raise exceptions that would prevent the primary operation from completing
2. Email sending operations must be handled asynchronously to avoid blocking user operations
3. Search index updates must be resilient to temporary service unavailability
4. Data cleanup operations must be atomic to prevent orphaned records
5. Callback execution must not significantly impact response times for user-facing operations
6. All callback operations must be idempotent to handle potential retry scenarios

## References

See context.md for existing user management patterns and callback implementations used throughout the application.