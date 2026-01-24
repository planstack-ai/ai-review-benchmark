# Nested Transaction Management for Order Processing

## Overview

The system needs to handle complex order processing workflows that involve multiple database operations across different models. These operations must be wrapped in nested transactions to ensure data consistency, with proper rollback behavior when any part of the process fails. The feature supports scenarios where an outer transaction manages the overall order state while inner transactions handle specific operations like inventory updates, payment processing, and notification logging.

## Requirements

1. The system must support nested database transactions using Rails transaction blocks
2. Inner transactions must properly roll back without affecting the outer transaction when using savepoints
3. The system must handle transaction rollback when any operation within a nested transaction fails
4. All database operations within a transaction block must be atomic - either all succeed or all fail
5. The system must properly propagate exceptions from inner transactions to outer transaction handlers
6. Transaction nesting must work correctly with ActiveRecord model validations and callbacks
7. The system must maintain data consistency across multiple related models during complex operations
8. Rollback behavior must be predictable and not leave the database in an inconsistent state

## Constraints

1. Maximum transaction nesting depth should not exceed 3 levels to avoid database limitations
2. Long-running transactions must be avoided to prevent database lock contention
3. Transaction blocks must not contain external API calls that could cause timeouts
4. Savepoint names must be unique within the same transaction scope
5. Database connections must be properly managed and not leaked during transaction failures

## References

See context.md for existing transaction handling patterns and database configuration details.