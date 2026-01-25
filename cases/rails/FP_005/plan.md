# Order Processing Service with Callbacks

## Overview

The system needs an order processing service that orchestrates the complete order lifecycle: validation, payment processing, inventory updates, and notifications. The service should use ActiveModel::Callbacks to provide hook points for each phase of processing, enabling extensibility and clear separation of concerns.

## Requirements

1. Validate order data before processing (order exists, user exists, items present)
2. Check inventory availability before proceeding with payment
3. Calculate order totals including subtotal, tax, and shipping costs
4. Process payment through external payment gateway
5. Update order status upon successful payment
6. Deduct inventory after successful order confirmation
7. Send confirmation email to customer asynchronously
8. Provide callback hooks for process, validation, and payment phases

## Business Rules

1. Shipping is free for orders over $100
2. International shipping costs $25, domestic shipping costs $10
3. Tax rate defaults to 8% unless shipping address specifies otherwise
4. Payment processing should only occur if payment_method is provided
5. Inventory must be validated before attempting payment

## Constraints

1. All database operations must be wrapped in a transaction for atomicity
2. Exceptions during processing should return a failure result, not crash
3. Email sending must be asynchronous (deliver_later)
4. Shipping cost calculation must use the current subtotal, not stale data
5. Callbacks must execute in the correct order: validate → payment → notification

## References

See context.md for Order, OrderItem, Product models and external service interfaces.
