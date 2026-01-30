# Job Outside After Commit - Order Notification System

## Overview

The system needs to send notifications to customers after their orders are successfully saved to the database. This involves dispatching background jobs that handle email notifications, ensuring that notifications are only sent when the database transaction has been committed successfully. The feature must handle order creation and updates while maintaining data consistency and preventing duplicate or premature notifications.

## Requirements

1. Create a background job that sends order confirmation notifications to customers
2. Dispatch the notification job automatically when an order is created or updated
3. Ensure the job is only executed after the database transaction has been successfully committed
4. Include order details (order ID, customer email, order total) in the notification
5. Handle both new order creation and existing order updates with the same notification mechanism
6. Implement proper error handling for failed notification attempts
7. Use Laravel's queue system for asynchronous job processing
8. Ensure notifications are sent only once per order save operation
9. Include customer name and order items in the notification payload
10. Set appropriate job retry attempts and failure handling

## Constraints

1. Notifications must not be sent if the database transaction fails or is rolled back
2. The job must not execute immediately within the same database transaction
3. Customer email must be validated before attempting to send notifications
4. Order must have a valid status before triggering notifications
5. Duplicate notifications for the same order operation must be prevented
6. The system must handle cases where the order is deleted before the job executes
7. Job execution must be resilient to temporary email service outages
8. Notification content must include all required order information at the time of job creation

## References

See context.md for existing Laravel job implementations and database transaction patterns in the codebase.