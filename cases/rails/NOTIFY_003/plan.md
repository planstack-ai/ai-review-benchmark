# Payment Confirmation Notification System

## Overview

The system must send confirmation notifications to users after their payment has been successfully confirmed. This ensures users receive timely acknowledgment of completed transactions and maintains transparency in the payment process. The notification should be triggered only when payment status changes to confirmed, not during intermediate processing states.

## Requirements

1. Send a notification immediately when a payment status changes to "confirmed"
2. Include payment amount, transaction ID, and confirmation timestamp in the notification
3. Send notifications to the email address associated with the payment account
4. Log all notification attempts with success/failure status
5. Handle notification delivery failures gracefully without affecting payment processing
6. Ensure notifications are sent only once per payment confirmation
7. Include a unique notification ID for tracking purposes
8. Set notification priority to "high" for payment confirmations
9. Use the standard notification template for payment confirmations
10. Record the notification timestamp in the payment record

## Constraints

1. Do not send notifications for payments in "pending" or "processing" states
2. Do not send duplicate notifications if payment status is updated multiple times to "confirmed"
3. Notification must be sent within 30 seconds of payment confirmation
4. If email address is invalid or missing, log error but do not retry notification
5. Maximum of 3 retry attempts for failed notification deliveries
6. Notifications should not be sent for payments below $0.01
7. System must handle concurrent payment confirmations without sending duplicate notifications

## References

See context.md for existing notification infrastructure, payment models, and related service implementations.