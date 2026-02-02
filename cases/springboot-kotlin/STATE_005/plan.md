# Partial Order Cancellation Service

## Overview

This service implements partial order cancellation for an e-commerce platform. Customers can cancel individual items from their order while keeping other items, and the order total must be recalculated correctly.

## Requirements

1. Allow cancellation of individual items from an order
2. Recalculate order total after partial cancellation
3. Update shipping fee if applicable based on new total
4. Restore cancelled item stock to inventory
5. Create cancellation record for audit trail
6. Handle refund calculation for cancelled items
7. Maintain order integrity during partial cancellation
8. Support cancellation of multiple items in one request

## Constraints

1. Cannot cancel items from shipped orders
2. Order total must reflect remaining items accurately
3. Discounts must be recalculated based on remaining items
4. At least one item must remain in the order
5. The service should be transactional
6. Cancelled items cannot be uncancelled

## References

See context.md for existing order management patterns in the codebase.
