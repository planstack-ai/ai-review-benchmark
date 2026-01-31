# Queue Connection Sync for Background Order Processing

## Overview

The system needs to process customer orders asynchronously using Laravel's queue system to improve application performance and user experience. When a customer places an order, the order processing should be handled in the background while immediately returning a success response to the user. The queue connection must be properly configured to ensure reliable job processing and maintain data consistency across the application.

## Requirements

1. Configure a queue connection named 'orders' that uses the sync driver for immediate processing during development
2. Create a job class that handles order processing logic including inventory updates and payment processing
3. Dispatch the order processing job to the 'orders' queue connection when an order is created
4. Ensure the job receives the complete order data including customer information, items, and payment details
5. Implement proper error handling within the job to catch and log processing failures
6. Update the order status to 'processing' when the job starts and 'completed' when finished successfully
7. Send order confirmation email to the customer after successful processing
8. Log all order processing activities for audit purposes
9. Ensure the queue worker can process jobs from the 'orders' connection
10. Maintain transactional integrity when updating order status and inventory levels

## Constraints

1. The sync driver must only be used in development environment
2. Order processing must complete within 30 seconds to prevent timeout issues
3. Failed jobs should not retry more than 3 times
4. Order status updates must be atomic to prevent race conditions
5. Customer email must be validated before sending confirmation
6. Inventory levels cannot go below zero during processing
7. Payment processing failures must rollback any inventory changes
8. Job payload must not exceed 65KB in size

## References

See context.md for existing queue configuration patterns and job implementation examples used throughout the application.