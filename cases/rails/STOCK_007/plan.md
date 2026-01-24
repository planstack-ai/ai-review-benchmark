# Duplicate Stock Restoration Prevention

## Overview

When orders are cancelled in an e-commerce system, the stock quantities for the associated products must be restored to make them available for future purchases. However, due to various system events, race conditions, or user actions, the same order cancellation might be processed multiple times. This creates a critical business problem where stock quantities can be incorrectly inflated, leading to overselling and inventory discrepancies.

This feature ensures that stock restoration occurs exactly once per order cancellation, regardless of how many times the cancellation process is triggered.

## Requirements

1. Stock quantities must be restored when an order is cancelled
2. Stock restoration must occur exactly once per order, even if cancellation is processed multiple times
3. The system must track which orders have already had their stock restored
4. Subsequent cancellation attempts on the same order must not modify stock quantities
5. The stock restoration process must be atomic to prevent partial updates
6. All line items in an order must have their stock restored together or not at all
7. The system must handle concurrent cancellation requests for the same order safely
8. Stock restoration must only occur for orders that were previously in a confirmed or shipped state
9. The restoration amount must match the exact quantity that was originally reserved/deducted

## Constraints

1. Orders in draft or already cancelled states should not trigger stock restoration
2. The system must prevent negative stock quantities after restoration
3. Stock restoration must fail gracefully if product records are missing or invalid
4. The tracking mechanism must persist across system restarts and deployments
5. Cancellation requests must be idempotent from a stock management perspective

## References

See context.md for existing order management and inventory tracking implementations.