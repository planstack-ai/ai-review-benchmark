# Order Payment Processing Service

## Overview

Implement a payment processing service that handles the complete payment flow for orders. The service must update order status, charge the customer via payment gateway, and record the payment reference. All database state changes must be atomic to prevent inconsistent order states.

## Requirements

1. Update order status to "processing" before initiating payment
2. Call the PaymentGateway to charge the order total amount
3. On successful payment, update order status to "paid" and store payment reference
4. On payment failure, the order should remain in its original state
5. Ensure database consistency - partial updates must not be persisted
6. Handle payment gateway exceptions gracefully

## Constraints

1. Order status transitions must be atomic - no partial state updates
2. Payment reference must be stored alongside status update
3. Failed payments must not leave orders in "processing" state permanently
4. The service must use the existing PaymentGateway interface

## References

See context.md for Order model and PaymentGateway interface details.
