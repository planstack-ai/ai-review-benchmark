# Order Refund Notification Email System

## Overview

The system needs to send refund confirmation emails to customers when their order refunds are processed. This is a critical privacy and security feature as refund notifications contain sensitive financial information and must be sent exclusively to the customer who owns the order. The system must ensure that email recipients are correctly identified and that no cross-customer data leakage occurs due to variable scope issues or incorrect references.

## Requirements

1. Send refund confirmation emails when refunds are successfully processed
2. Ensure email is sent only to the customer who owns the refunded order
3. Include refund details (amount, refund method, transaction reference)
4. Include original order information for customer reference
5. Verify customer identity before sending sensitive financial information
6. Log all refund notification sends with customer and order identifiers
7. Handle cases where multiple refunds may be processed simultaneously
8. Use proper variable scoping to prevent recipient mixups
9. Validate email recipient matches the order owner
10. Provide audit trail for all refund notifications sent

## Constraints

1. Email must be sent only to the order owner's email address
2. No cross-customer email delivery is acceptable (critical privacy violation)
3. Variable scope must be carefully managed to prevent wrong recipient selection
4. Each refund notification must use the correct order's customer email
5. System must prevent using administrator or processor email by mistake
6. All email sends must include validation that recipient matches order owner
7. Concurrent refund processing must not cause recipient confusion

## References

See context.md for existing database schema, entity definitions, refund processing service, and email infrastructure.
