# Partial Order Cancellation with Total Recalculation

## Overview

The system must handle partial cancellation of order items while maintaining accurate order totals. When customers cancel specific items from an order (rather than the entire order), the system needs to update the order's financial totals to reflect only the remaining active items. This ensures billing accuracy and proper inventory management for partially fulfilled orders.

## Requirements

1. The system shall allow cancellation of individual line items within an order
2. When a line item is cancelled, its status shall be updated to "cancelled"
3. The order's total amount shall be recalculated to exclude all cancelled line items
4. The order's subtotal shall reflect only the sum of remaining active line items
5. Tax calculations shall be updated based on the new subtotal of active items
6. The order's item count shall reflect only non-cancelled items
7. Cancelled items shall remain in the order record for audit purposes
8. The system shall persist all changes to the database in a single transaction
9. Order status shall remain "active" if any line items are still active
10. Order status shall change to "cancelled" only if all line items are cancelled

## Constraints

1. Only line items with status "pending" or "confirmed" can be cancelled
2. Line items that are already "shipped" or "delivered" cannot be cancelled
3. Partial cancellations are not allowed - entire line item quantities must be cancelled
4. The order total must never be negative after cancellation
5. At least one line item must remain active unless cancelling the entire order
6. Cancellation operations must be atomic - either all updates succeed or none do

## References

See context.md for existing Order and LineItem model implementations and current cancellation workflows.