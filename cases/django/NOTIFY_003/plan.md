# Payment Confirmation Notification System

## Overview

The system needs to handle payment confirmation notifications to users after their payments have been successfully processed. This feature ensures users receive timely confirmation of their financial transactions through the application's notification system. The notification should be triggered automatically when a payment status changes to confirmed, providing users with immediate feedback about their transaction status.

## Requirements

1. The system must send a notification when a payment status changes to "confirmed"
2. The notification must be sent only after the payment confirmation is complete and persisted
3. The notification must include relevant payment details (amount, transaction ID, timestamp)
4. The notification must be sent to the user who made the payment
5. The system must handle the notification sending asynchronously to avoid blocking the payment confirmation process
6. The notification must be sent exactly once per payment confirmation to avoid duplicate notifications
7. The system must log successful notification deliveries for audit purposes
8. The notification content must be user-friendly and include clear confirmation messaging

## Constraints

1. Notifications must not be sent for payments in "pending", "failed", or "cancelled" states
2. The system must not send notifications if the user has disabled payment notifications in their preferences
3. Notification sending must not interfere with or delay the payment confirmation process
4. The system must handle notification delivery failures gracefully without affecting payment processing
5. Payment confirmation must be atomic - either the payment is confirmed and notification is queued, or neither occurs
6. The system must validate that the payment belongs to an active user account before sending notifications

## References

See context.md for existing payment processing models, notification infrastructure, and user preference management implementations.