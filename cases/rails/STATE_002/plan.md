# Order Cancellation Window Implementation

## Overview

The system must provide customers with the ability to cancel their orders, but only within a specific time window to ensure operational efficiency and prevent cancellations of orders that have already entered the fulfillment process. This feature protects both customer satisfaction and business operations by establishing clear boundaries around when cancellations are permitted.

## Requirements

1. Orders must be cancellable by customers through the system interface
2. Cancellation must only be permitted before the order has been shipped
3. The system must check the current shipment status before allowing any cancellation attempt
4. When an order is successfully cancelled, the order status must be updated to "cancelled"
5. Cancelled orders must not proceed to shipment or any further processing stages
6. The system must provide clear feedback when a cancellation attempt is made
7. Cancellation attempts on already shipped orders must be rejected with appropriate messaging
8. The cancellation feature must be accessible through the order management interface

## Constraints

1. Orders with status "shipped" or "delivered" cannot be cancelled under any circumstances
2. The shipment status check must be performed at the time of cancellation request, not cached
3. Cancellation requests must be processed atomically to prevent race conditions
4. The system must handle concurrent cancellation attempts gracefully
5. Orders that are currently being processed for shipment may have timing-dependent cancellation availability

## References

See context.md for existing order management system structure and current implementation patterns.