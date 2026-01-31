# Payment Confirmation Email Notification System

## Overview

The system needs to send order completion confirmation emails to customers after successful payment processing. This notification is critical for customer experience and must only be sent after the payment transaction has been fully committed to the database. The system must ensure that emails are not sent prematurely, before payment confirmation is complete, which could lead to customer confusion or incorrect order status communication.

## Requirements

1. Send order completion confirmation emails after payment is confirmed
2. Ensure email is only sent after database transaction commit completes
3. Use Spring's transactional event listeners to coordinate timing
4. Include payment confirmation details in the email (transaction ID, amount paid, payment method)
5. Handle cases where payment is successful but email sending fails
6. Prevent sending duplicate emails if the event is triggered multiple times
7. Log all email sending attempts with transaction context
8. Ensure email content reflects the final committed state of the order
9. Support both synchronous and asynchronous email delivery
10. Provide proper error handling for email service failures

## Constraints

1. Email must never be sent before payment transaction commits
2. Payment confirmation must be persisted before email is triggered
3. Email content must use the committed transaction data only
4. System must handle transaction rollback scenarios gracefully
5. Email should not cause the payment transaction to fail or rollback
6. Notification timing must be coordinated with Spring's transaction lifecycle
7. Event listeners must be properly configured with the correct phase

## References

See context.md for existing database schema, entity definitions, payment service, and email infrastructure.
