# SPRING_012: Send notification after order saved

## Overview

Implement order confirmation notification system that sends email notification after order is successfully saved to the database.

## Requirements

1. Save order to database
2. Send confirmation email asynchronously to avoid blocking the request
3. Email should include order details (order ID, total amount, items)
4. Ensure notification is sent only after order is committed to database

## Constraints

- Use Spring's `@Async` for asynchronous email sending
- Transaction should commit successfully before notification
- Email service should not block the order creation response
- Notification should reference valid, committed order data

## References

- Spring `@Async` documentation
- Spring transaction management
- Asynchronous processing in Spring Boot
