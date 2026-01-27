# Order Service with Status Transition Validation

## Overview

This service manages order lifecycle including creation and status updates. Status transitions are validated against a database-driven configuration with fallback to default transitions defined in OrderConstants. The system ensures only valid state transitions are allowed.

## Requirements

1. Implement order creation with customer ID and total amount
2. Implement order status update with transition validation
3. Implement method to get all allowed transitions from a given status
4. Implement method to check if a specific transition is allowed
5. Status transition validation first checks OrderStatusTransitionRepository
6. If no database configuration exists, fall back to OrderConstants.DEFAULT_TRANSITIONS
7. Throw IllegalStateException for invalid status transitions
8. Use constructor injection for dependencies

## Constraints

1. All operations must be transactional (@Transactional at class level)
2. Customer ID must be positive (throw IllegalArgumentException if null or <= 0)
3. Total amount cannot be negative (throw IllegalArgumentException if null or < 0)
4. Order must exist for status update (throw IllegalArgumentException if not found)
5. New orders start with PENDING status
6. getAllowedTransitions returns empty list if no transitions are configured
7. isTransitionAllowed returns false if transition is not explicitly allowed

## References

See context.md for Order entity, OrderStatus enum, OrderStatusTransition entity, OrderConstants.DEFAULT_TRANSITIONS, and repository interfaces.
