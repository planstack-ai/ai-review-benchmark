# Order Partial Cancellation with Total Integrity

## Overview

The system must handle partial cancellation of orders while maintaining accurate financial totals. When a customer cancels only some items from their order, the system needs to update the order total to reflect the remaining items while preserving the integrity of the original order data and maintaining proper audit trails.

## Requirements

1. The system must allow partial cancellation of order items within an existing order
2. When items are partially cancelled, the order total must be recalculated based on remaining active items
3. The system must preserve the original order total for audit purposes
4. Cancelled items must be marked with appropriate status while remaining items stay active
5. The order status must reflect partial cancellation state when some but not all items are cancelled
6. All total calculations must account for taxes, discounts, and shipping costs proportionally
7. The system must prevent cancellation of items that have already been shipped or delivered
8. Partial cancellation operations must be atomic to prevent data inconsistency
9. The system must maintain a history of cancellation events with timestamps and reasons
10. Order totals must be updated immediately upon successful partial cancellation

## Constraints

- Cannot cancel items with status "shipped" or "delivered"
- Cannot cancel more quantity than originally ordered for any item
- Order total cannot become negative after partial cancellation
- Minimum order value rules must be respected after cancellation
- Cancellation must fail if it would violate business rules (e.g., minimum order requirements)
- All monetary calculations must maintain precision to avoid rounding errors
- Concurrent partial cancellations on the same order must be handled safely

## References

See context.md for existing order management system implementation details and database schema.