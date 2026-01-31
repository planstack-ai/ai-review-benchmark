# SPRING_014: Find or create order record

## Overview

Implement idempotent order creation that prevents duplicate orders from external system by checking external order ID.

## Requirements

1. Accept orders from external system with external order ID
2. Check if order with external ID already exists
3. If exists, return existing order
4. If not exists, create new order
5. Ensure no duplicate orders are created even under concurrent requests

## Constraints

- Orders from same external system should have unique external_id
- Multiple concurrent requests with same external_id should not create duplicates
- System should handle high concurrency (multiple threads/processes)
- Response should be fast (avoid long locks if possible)

## References

- JPA locking mechanisms
- Database unique constraints
- Optimistic vs pessimistic locking
