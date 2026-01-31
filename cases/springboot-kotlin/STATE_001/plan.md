# Order Cancellation State Management

## Overview

This system manages order state transitions with specific business rules governing when orders can be cancelled. The order lifecycle includes multiple states, and cancellation is only permitted during specific phases of the order processing workflow to maintain business integrity and operational consistency.

## Requirements

1. Define an Order entity with appropriate state management capabilities
2. Implement state enumeration covering the complete order lifecycle (PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED)
3. Create a cancellation method that validates current state before allowing transition
4. Ensure cancellation is only permitted when order state is PENDING or CONFIRMED
5. Throw appropriate exception when cancellation is attempted from invalid states
6. Maintain state transition history for audit purposes
7. Provide clear error messaging indicating why cancellation failed
8. Implement proper validation before any state change occurs
9. Ensure cancelled orders cannot be modified further
10. Create REST endpoint to handle cancellation requests with proper HTTP status codes

## Constraints

- Orders in SHIPPED state cannot be cancelled (goods already in transit)
- Orders in DELIVERED state cannot be cancelled (transaction complete)
- Orders already in CANCELLED state should not allow re-cancellation
- State transitions must be atomic and thread-safe
- Invalid state transition attempts must not modify the order
- Cancellation timestamp must be recorded when transition occurs
- Original order data must remain intact after cancellation

## References

See context.md for existing codebase patterns and architectural decisions.