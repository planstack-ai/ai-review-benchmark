# Order Cancellation State Management

## Overview

This system manages order state transitions with specific business rules governing when orders can be cancelled. The order lifecycle includes multiple states, and cancellation is only permitted during specific phases of the order processing workflow to maintain business integrity and operational consistency.

## Requirements

1. Orders must maintain a current state that can be tracked and validated
2. Order cancellation must be restricted to only PENDING and CONFIRMED states
3. Attempting to cancel an order from any other state must result in an appropriate error response
4. The system must validate the current order state before processing any cancellation request
5. State transition validation must occur before any cancellation logic is executed
6. The cancellation operation must update the order state to CANCELLED when successful
7. All state transitions must be atomic to prevent inconsistent states
8. The system must provide clear feedback when cancellation is not permitted due to state restrictions

## Constraints

1. Orders in SHIPPED, DELIVERED, or already CANCELLED states cannot be cancelled
2. State validation must be performed using the current state at the time of the cancellation request
3. Concurrent state changes must be handled appropriately to prevent race conditions
4. Invalid state transition attempts must not modify the order in any way
5. The system must maintain referential integrity during state transitions

## References

See context.md for existing order management implementations and state handling patterns.