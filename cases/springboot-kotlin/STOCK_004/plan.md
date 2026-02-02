# Reserved vs Available Stock Tracking

## Overview

This system manages inventory for an e-commerce platform that uses a reservation model. When customers add items to their cart or begin the checkout process, stock is temporarily reserved to ensure availability. The system must track both total stock and reserved stock separately to accurately report available stock for new customers. Available stock is the difference between total stock and currently reserved quantities.

## Requirements

1. The system shall maintain separate tracking for total stock and reserved stock quantities
2. Available stock must be calculated as total stock minus reserved stock
3. The system shall provide an endpoint to check available stock for a product
4. Reserved stock quantities must be tracked per product
5. When calculating available stock for new orders, the system must exclude already reserved quantities
6. The system shall prevent overselling by accounting for pending reservations
7. Stock reservations must be tracked with timestamps and reservation IDs
8. The available stock calculation must be accurate even under concurrent access
9. The system shall handle multiple concurrent reservations for the same product
10. Available stock queries must return real-time accurate values

## Constraints

1. Total stock quantity must always be greater than or equal to reserved stock
2. Available stock cannot be negative
3. Product IDs must be valid and exist in the system
4. Reserved quantities must be positive integers
5. The system must handle concurrent stock queries and reservations correctly
6. Database operations must maintain consistency between total and reserved stock

## References

See context.md for existing stock management implementations, reservation tracking, and database schema details.
