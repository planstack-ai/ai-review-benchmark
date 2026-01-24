# Rails Callback Order Dependency Management

## Overview

This system manages user account lifecycle events through Rails model callbacks. The business requires specific sequencing of operations when user accounts are created, updated, or destroyed to ensure data integrity, proper audit trails, and correct notification delivery. The callback chain must execute in a predetermined order to maintain consistency across user management workflows and prevent race conditions in dependent systems.

## Requirements

1. User creation must trigger welcome email notification after profile setup is complete
2. Profile validation must occur before any external service notifications are sent
3. Audit logging must capture the final state after all data transformations are applied
4. Cache invalidation must happen after database commits are successful
5. External API notifications must be sent only after local data consistency is verified
6. User deletion must revoke access tokens before removing user data
7. Account status changes must update dependent records before triggering notifications
8. Callback execution must be atomic - if any callback fails, the entire operation should rollback
9. System must maintain callback execution order regardless of callback registration sequence
10. Error handling must preserve the callback chain integrity and provide meaningful failure context

## Constraints

- Callbacks must not create circular dependencies between models
- External service calls within callbacks must have timeout protection
- Database transactions must encompass the entire callback chain
- Callback failures must not leave the system in an inconsistent state
- Performance impact of callback chains must not exceed 500ms for standard operations
- Callback order must be deterministic and testable
- System must handle callback exceptions gracefully without breaking the chain

## References

See context.md for existing callback implementations and current system architecture patterns.