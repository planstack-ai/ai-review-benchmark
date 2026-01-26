# Complex Nested Transaction Management System

## Overview

This system implements a financial transaction processing service that handles complex nested database transactions for account transfers, audit logging, and notification systems. The service must ensure data consistency across multiple related operations while maintaining proper transaction boundaries and rollback capabilities.

## Requirements

1. Implement a transaction service that supports nested savepoints for multi-step financial operations
2. Create account transfer functionality that atomically updates both source and destination account balances
3. Implement audit logging that records all transaction attempts within the same database transaction
4. Provide notification queuing that integrates with the transaction lifecycle
5. Support partial rollback scenarios where outer transactions can continue after inner transaction failures
6. Implement proper exception handling that maintains transaction integrity
7. Create transaction status tracking that persists across nested transaction boundaries
8. Ensure all database operations use appropriate transaction isolation levels
9. Implement cleanup procedures for failed nested transactions
10. Provide transaction metrics and logging for monitoring purposes

## Constraints

1. All financial operations must be atomic - either all related changes succeed or all fail
2. Account balances cannot become negative during any point in the transaction
3. Audit logs must be created even if the main transaction fails, using separate transaction contexts
4. Nested transactions must properly release savepoints to avoid resource leaks
5. Transaction timeouts must be configurable and enforced at each nesting level
6. Concurrent access to the same accounts must be handled with appropriate locking
7. System must handle database connection failures gracefully during nested operations
8. All monetary calculations must maintain precision to avoid rounding errors

## References

See context.md for existing database models, transaction utilities, and related service implementations that this system should integrate with.