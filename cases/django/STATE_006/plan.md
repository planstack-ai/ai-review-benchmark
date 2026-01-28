# Payment Refund Status Management

## Overview

The payment system needs to properly track and update payment status when refunds are processed. When a refund is initiated for a payment, the system must ensure that the payment's status is updated to reflect the refund state, maintaining data consistency and providing accurate payment history for business operations and customer inquiries.

## Requirements

1. When a refund is created for a payment, the associated payment's status must be updated to "refunded"
2. The refund creation process must be atomic - both refund creation and payment status update must succeed or fail together
3. Only payments with status "completed" or "captured" should be eligible for refunds
4. The system must prevent duplicate refunds for the same payment
5. Refund amounts must not exceed the original payment amount
6. The payment status update must occur immediately when the refund is successfully created
7. All refund operations must be logged for audit purposes
8. The refund process must handle partial refunds by updating payment status to "partially_refunded"
9. When the total refunded amount equals the original payment amount, the payment status must be "fully_refunded"

## Constraints

1. Refund amounts must be positive decimal values
2. Payment status transitions must follow the defined state machine rules
3. Refunds cannot be created for payments that are already in "refunded" or "cancelled" status
4. The system must validate that the payment exists and belongs to the requesting user before processing refunds
5. Concurrent refund requests for the same payment must be handled safely to prevent race conditions
6. Database integrity must be maintained even if the refund process is interrupted

## References

See context.md for existing payment and refund model implementations and current status handling patterns.