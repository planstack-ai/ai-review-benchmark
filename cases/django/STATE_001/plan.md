# Order State Transition Validation System

## Overview

An e-commerce order management system requires strict control over order state transitions to maintain data integrity and business logic consistency. Orders must follow a predefined workflow where certain state changes are permitted while others are forbidden. The system must prevent invalid transitions that could lead to business process violations, such as shipping a cancelled order or refunding an order that hasn't been paid.

## Requirements

1. Define a comprehensive set of valid order states including pending, confirmed, paid, shipped, delivered, cancelled, and refunded
2. Establish a state transition matrix that specifies which state changes are permitted from each current state
3. Implement validation logic that prevents any state transition not explicitly allowed in the transition matrix
4. Raise appropriate exceptions when invalid state transitions are attempted
5. Ensure state transitions are atomic and cannot leave orders in inconsistent states
6. Log all state transition attempts for audit purposes
7. Provide clear error messages indicating why a specific transition was rejected
8. Support querying orders by their current state for reporting and workflow management
9. Maintain historical records of all state changes with timestamps
10. Ensure the system handles concurrent state change attempts safely

## Constraints

1. Orders in "delivered" state cannot transition to any other state except "refunded"
2. Orders cannot transition directly from "pending" to "shipped" without going through "confirmed" and "paid" states
3. Cancelled orders cannot be reactivated or moved to any active state
4. Refunded orders represent a terminal state with no further transitions allowed
5. State transitions must be validated before any database changes are committed
6. The system must handle edge cases where multiple users attempt to change the same order state simultaneously
7. All state changes must be reversible through proper business processes (except for terminal states)

## References

See context.md for existing Django model implementations and related order management functionality.