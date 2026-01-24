# Complex Nested Transaction Management System

## Overview

This system manages financial transactions that require complex nested transaction handling with proper rollback capabilities. The business context involves processing multi-step financial operations where each step must be atomic, and the entire operation must maintain data consistency across multiple database tables. The system handles scenarios where inner transactions may need to rollback independently while preserving outer transaction integrity.

## Requirements

1. Implement a transaction processing service that supports nested transactions with at least 3 levels of nesting
2. Each transaction level must maintain its own rollback capability without affecting parent transactions
3. The system must handle concurrent access to shared resources within nested transactions
4. Transaction state must be properly tracked and logged at each nesting level
5. Failed inner transactions must not automatically rollback outer transactions unless explicitly configured
6. The system must support savepoints for partial rollback scenarios
7. All transaction operations must be wrapped in proper exception handling with specific error types
8. Transaction isolation levels must be configurable per transaction level
9. The system must provide transaction status reporting for monitoring and debugging
10. Database connections must be properly managed and released after transaction completion

## Constraints

1. Maximum transaction nesting depth is limited to 5 levels to prevent stack overflow
2. Transaction timeout must not exceed 30 seconds for any single transaction level
3. Savepoint names must be unique within the same transaction scope
4. Concurrent transaction limit is 100 active transactions per application instance
5. Transaction logs must be persisted even if the main transaction fails
6. Memory usage for transaction state tracking must not exceed 10MB per transaction tree
7. All monetary calculations must maintain precision to 4 decimal places
8. Transaction rollback must complete within 5 seconds or trigger an alert

## References

See context.md for existing transaction handling patterns and database configuration requirements.