# Order Confirmation Email Deduplication System

## Overview

The system must ensure that customers receive exactly one order confirmation email per order, regardless of how many times the order confirmation process is triggered. This prevents customer confusion and maintains professional communication standards while avoiding email spam issues.

## Requirements

1. Each order must generate exactly one confirmation email to the customer
2. The system must track which orders have already had confirmation emails sent
3. Subsequent attempts to send confirmation emails for the same order must be prevented
4. The email sending mechanism must be idempotent across multiple invocations
5. Order confirmation emails must contain standard order details (order number, items, total, customer information)
6. The system must handle concurrent requests for the same order confirmation gracefully
7. Email sending status must be persistently stored and retrievable
8. Failed email attempts should not prevent retry mechanisms for legitimate cases
9. The confirmation email functionality must integrate with Django's email backend
10. Order status changes that don't require new emails must not trigger duplicate sends

## Constraints

1. Only completed/confirmed orders should trigger confirmation emails
2. Draft or cancelled orders must not generate confirmation emails
3. The system must distinguish between order updates and initial order confirmation
4. Email addresses must be validated before sending attempts
5. The deduplication mechanism must survive application restarts
6. Database transactions must ensure consistency between order state and email tracking
7. The system must handle cases where email service is temporarily unavailable

## References

See context.md for existing Django model structures, email service configurations, and current order processing workflow implementations.