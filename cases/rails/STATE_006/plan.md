# Payment Refund Status Update Implementation

## Overview

The payment system needs to properly handle refund processing by updating the payment status when a refund is successfully processed. This ensures that the payment record accurately reflects its current state and maintains data consistency across the system. The refund process should transition payments from their current status to a refunded state, allowing other parts of the system to properly handle refunded payments.

## Requirements

1. When a refund is successfully processed, the payment status must be updated to reflect the refunded state
2. The payment status update must occur within the same transaction as the refund processing to ensure data consistency
3. The system must handle partial refunds by updating the payment status appropriately
4. The system must handle full refunds by updating the payment status to indicate complete refund
5. Status updates must be persisted to the database before the refund operation is considered complete
6. The refund amount must be validated against the original payment amount before processing
7. Only payments in valid states should be eligible for refund processing

## Constraints

1. Refund amounts cannot exceed the original payment amount
2. Payments that are already fully refunded cannot be refunded again
3. Cancelled or failed payments cannot be refunded
4. The refund operation must be atomic - either all updates succeed or all fail
5. Status transitions must follow valid state machine rules
6. Concurrent refund attempts on the same payment must be handled safely

## References

See context.md for existing payment model structure, status enumeration values, and current refund processing workflow.