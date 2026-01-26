# External API Call Transaction Management

## Overview

The system needs to integrate with external payment processing services to handle customer transactions. When processing orders, the application must communicate with third-party APIs to validate payments, update inventory systems, and send notifications. These external API calls must be properly managed in relation to database transactions to ensure data consistency and prevent issues like duplicate charges or inconsistent state when external services fail or respond slowly.

## Requirements

1. External API calls must be executed outside of database transactions
2. Database operations must be committed before making external API calls
3. If external API calls fail, the system must handle the failure gracefully without rolling back already-committed database changes
4. The system must implement proper error handling for external API failures
5. External API calls must not block or delay database transaction commits
6. The implementation must prevent scenarios where database rollbacks occur after external APIs have already been called
7. All external service integrations (payment processing, inventory updates, notifications) must follow the same transaction isolation pattern
8. The system must maintain data consistency even when external services are unavailable or respond with errors

## Constraints

1. Database transactions must not remain open while waiting for external API responses
2. External API timeouts must not cause database connection pool exhaustion
3. Failed external API calls must not trigger automatic database rollbacks
4. The system must handle partial failures where some external APIs succeed and others fail
5. Network latency from external APIs must not impact database performance
6. External API calls must be idempotent to handle retry scenarios safely

## References

See context.md for existing codebase patterns and current implementation approaches.