# Django Async Notification Error Handling System

## Overview

The system needs to handle background notification jobs that may fail during execution. When notifications are processed asynchronously (such as email sending, SMS delivery, or push notifications), failures must be properly captured, logged, and handled to ensure system reliability and user awareness. The system should provide mechanisms to track notification delivery status and handle various failure scenarios gracefully.

## Requirements

1. All async notification jobs must implement proper error handling and capture exceptions
2. Failed notification attempts must be logged with sufficient detail for debugging
3. The system must track notification delivery status (pending, sent, failed, retrying)
4. Failed notifications must trigger appropriate fallback mechanisms or retry logic
5. Critical notification failures must alert system administrators
6. The notification service must provide status reporting capabilities for monitoring
7. Database records must be updated to reflect the actual delivery status of notifications
8. Async job failures must not cause silent data inconsistencies
9. The system must handle network timeouts and external service unavailability
10. Failed notification jobs must not crash the background worker process

## Constraints

- Notification status updates must be atomic to prevent race conditions
- Retry attempts must implement exponential backoff to avoid overwhelming external services
- Failed notifications older than 7 days should be marked as permanently failed
- The system must handle partial failures in batch notification operations
- External service rate limits must be respected during retry attempts
- Notification failures must not expose sensitive user data in logs

## References

See context.md for existing notification service implementations and database schema details.