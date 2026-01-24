# Order Confirmation Email Deduplication System

## Overview

The system must ensure that customers receive exactly one order confirmation email per order, regardless of how many times the order confirmation process is triggered. This prevents customer confusion and maintains professional communication standards while avoiding email spam issues.

## Requirements

1. Each order must generate exactly one confirmation email to the customer
2. The system must track when an order confirmation email has been sent
3. Subsequent attempts to send confirmation emails for the same order must be prevented
4. The email sending mechanism must be idempotent for order confirmations
5. The system must handle concurrent order processing scenarios gracefully
6. Email sending status must be persisted and queryable
7. The system must provide clear logging when duplicate email attempts are blocked
8. Order confirmation emails must include all necessary order details and customer information

## Constraints

1. Email sending attempts must be atomic operations
2. The system must handle database transaction failures gracefully
3. Email delivery failures should not mark the email as "sent" 
4. The deduplication mechanism must work across application restarts
5. Performance impact of deduplication checks must be minimal
6. The system must distinguish between different types of order-related emails (confirmation vs. shipping updates)

## References

See context.md for existing email service implementations and order processing workflows.