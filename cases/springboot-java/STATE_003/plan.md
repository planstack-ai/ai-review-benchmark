# Stock Reservation System with Atomic Check-Then-Act Operations

## Overview

This system manages product inventory and handles stock reservations for an e-commerce platform. The core functionality involves checking available stock levels and reserving items atomically to prevent overselling in concurrent environments. The system must ensure that stock levels never go negative and that multiple simultaneous reservation requests are handled correctly without race conditions.

## Requirements

1. Implement a ProductService that manages product inventory with stock levels
2. Provide a method to reserve stock that first checks availability then decrements the quantity
3. Ensure the check-and-reserve operation is atomic to prevent race conditions
4. Return appropriate success/failure responses indicating whether reservation was successful
5. Maintain accurate stock levels that reflect all successful reservations
6. Handle concurrent reservation requests without allowing overselling
7. Provide a method to query current stock levels for products
8. Initialize products with configurable stock quantities
9. Support reservation of multiple units in a single operation
10. Ensure thread-safety across all stock operations

## Constraints

1. Stock levels must never become negative
2. Reservation requests for quantities exceeding available stock must be rejected
3. Reservation requests for zero or negative quantities must be rejected
4. Product must exist before stock operations can be performed
5. All stock operations must be atomic - no partial updates allowed
6. System must handle high concurrency without data corruption
7. Stock levels must be consistent across all concurrent operations

## References

See context.md for examples of existing implementations and common patterns used in similar stock management systems.