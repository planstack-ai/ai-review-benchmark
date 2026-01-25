# Django Task Queuing After Transaction Commit

## Overview

This feature implements a mechanism to queue background tasks that should only execute after a database transaction has successfully committed. This is critical for maintaining data consistency when background tasks depend on database changes made within a transaction. The system must ensure that tasks are not executed if the transaction fails or is rolled back.

## Requirements

1. Provide a function or decorator that allows queuing tasks to run after the current transaction commits
2. Tasks must only execute if the transaction commits successfully
3. Tasks must not execute if the transaction is rolled back or fails
4. Support queuing multiple tasks within a single transaction
5. Tasks should execute in the order they were queued
6. Handle cases where no active transaction exists
7. Integrate with Django's transaction management system
8. Support both function-based and class-based task definitions
9. Provide error handling for task execution failures
10. Ensure tasks execute outside of the original transaction context

## Constraints

1. Tasks queued outside of an active transaction should execute immediately
2. Nested transactions should properly handle task queuing at the appropriate commit level
3. Task execution failures should not affect the original transaction's success
4. Memory usage should be reasonable when queuing large numbers of tasks
5. The system should work with Django's various transaction decorators and context managers
6. Tasks should not have access to uncommitted transaction data
7. The implementation must be thread-safe for concurrent transaction handling

## References

See context.md for existing Django transaction handling patterns and background task integration examples.