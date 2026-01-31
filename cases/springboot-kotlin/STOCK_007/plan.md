# Idempotent Stock Restoration on Cancellation

## Overview

This system handles order cancellations in an e-commerce platform. When an order is cancelled, the system must restore the purchased inventory back to stock. However, due to potential network issues, duplicate API calls, or system retries, the same cancellation request might be processed multiple times. The system must ensure that stock is restored exactly once per cancellation, even if the cancellation endpoint is called multiple times for the same order.

## Requirements

1. The system shall provide an endpoint to cancel orders
2. When an order is successfully cancelled, stock quantities must be restored
3. The cancellation operation must be idempotent - calling it multiple times should have the same effect as calling it once
4. The system must track whether stock has already been restored for a cancelled order
5. Duplicate cancellation requests must not restore stock multiple times
6. The system shall return appropriate status indicating whether this is the first cancellation or a duplicate
7. Stock restoration state must be persisted at the order level
8. The implementation must handle concurrent cancellation requests for the same order
9. Clear audit logging must track stock restoration events
10. The system must prevent stock levels from becoming incorrect due to duplicate processing

## Constraints

1. Order IDs must be valid and reference existing orders
2. Only confirmed or pending orders can be cancelled initially
3. Stock restoration must be atomic with the order status update
4. The idempotency check must be reliable even under concurrent access
5. Database state must remain consistent if the process is interrupted
6. The system should use database fields or flags to track restoration status
7. The solution must not rely on external caching for idempotency

## References

See context.md for existing order cancellation implementations, stock management patterns, and database schema details.
