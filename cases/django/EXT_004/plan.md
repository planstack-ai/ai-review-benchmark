# Retry Duplicate Order Prevention System

## Overview

The system must handle order retry scenarios where customers attempt to resubmit orders that may have already been processed. This commonly occurs when users experience network timeouts, browser issues, or payment gateway delays, leading them to retry their order submission. The system needs to detect and prevent duplicate orders while maintaining a smooth user experience and ensuring legitimate retries are processed correctly.

## Requirements

1. The system must detect when an order submission is a potential duplicate based on customer identification and order details
2. When a duplicate order is detected, the system must return the existing order information instead of creating a new order
3. The system must validate that the retry request contains identical order details (items, quantities, pricing) to the original order
4. The system must implement a time window for considering orders as potential duplicates (e.g., within the last 30 minutes)
5. The system must handle concurrent order submissions from the same customer gracefully
6. The system must log all duplicate order detection events for audit purposes
7. The system must return appropriate HTTP status codes and response messages for duplicate order scenarios
8. The system must maintain order state consistency when handling retries
9. The system must support both authenticated and guest customer order scenarios
10. The system must validate customer identity before returning existing order information

## Constraints

1. Guest customers must be identified through a combination of email address and session information
2. Authenticated customers must be identified through their user account
3. Order comparison must include all critical order attributes (items, quantities, shipping address, payment method)
4. The duplicate detection window must not exceed 60 minutes to prevent legitimate reorders from being blocked
5. Price variations due to promotions or inventory changes must invalidate duplicate detection
6. Orders in failed or cancelled states must not prevent new order creation
7. The system must handle cases where the original order is still being processed
8. Database operations for duplicate detection must be atomic to prevent race conditions

## References

See context.md for existing order processing implementation patterns and database schema details.