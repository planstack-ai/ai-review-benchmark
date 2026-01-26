# Order Cancellation Window Implementation

## Overview

The system needs to implement a cancellation window for customer orders that prevents cancellation once an order has been shipped. This ensures that customers can only cancel orders while they are still in the fulfillment process and haven't left the warehouse. The feature protects against revenue loss from cancelled shipped orders while maintaining customer flexibility during the pre-shipment phase.

## Requirements

1. Orders must have a cancellation method that checks the current order status before allowing cancellation
2. Cancellation must be permitted only when the order status is "pending", "processing", or "confirmed"
3. Cancellation must be blocked when the order status is "shipped", "delivered", or "cancelled"
4. The cancellation method must update the order status to "cancelled" when cancellation is allowed
5. The cancellation method must return a boolean indicating success or failure of the cancellation attempt
6. The system must preserve the original order timestamp when cancellation occurs
7. Cancelled orders must retain all original order details for audit purposes

## Constraints

1. Orders that are already cancelled cannot be cancelled again
2. The cancellation window check must be performed atomically to prevent race conditions
3. Order status transitions must follow the defined workflow: pending → processing → confirmed → shipped → delivered
4. The system must handle edge cases where order status might be None or invalid
5. Cancellation attempts on non-existent orders should be handled gracefully

## References

See context.md for existing Order model structure and related implementations.