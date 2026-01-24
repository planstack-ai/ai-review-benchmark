# Retry Duplicate Order Prevention System

## Overview

When customers experience payment failures or network timeouts during order submission, they often retry their purchase attempt. This can lead to duplicate orders being created if the original order was actually processed successfully but the confirmation was not received by the client. The system must implement safeguards to detect and prevent duplicate order creation during retry scenarios while maintaining a smooth user experience.

## Requirements

1. The system must detect when an order submission is a potential retry attempt based on customer and order characteristics
2. Before creating a new order, the system must check for existing orders with identical or substantially similar details within a configurable time window
3. When a duplicate order attempt is detected, the system must return the details of the existing order instead of creating a new one
4. The duplicate detection must consider customer ID, product items, quantities, and total amount as matching criteria
5. The system must log all duplicate order prevention events for monitoring and debugging purposes
6. The duplicate check must be performed atomically to prevent race conditions in high-concurrency scenarios
7. The system must handle cases where the original order is in a failed or cancelled state by allowing the retry to proceed
8. Response times for duplicate detection must not significantly impact the normal order creation flow
9. The system must provide clear feedback to the client when a duplicate is detected versus when a new order is created

## Constraints

- Duplicate detection window must not exceed 24 hours to avoid blocking legitimate repeat purchases
- Only orders in 'pending', 'confirmed', or 'processing' states should block duplicate creation
- The system must handle partial matches gracefully (e.g., same items but different quantities)
- Database queries for duplicate detection must be optimized to prevent performance degradation
- The duplicate prevention mechanism must not interfere with legitimate bulk orders or subscription renewals

## References

See context.md for existing order creation workflows, database schema, and current validation implementations.