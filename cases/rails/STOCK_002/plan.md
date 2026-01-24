# Inventory Stock Management with Atomic Updates

## Overview

The inventory management system must handle concurrent stock updates safely to prevent overselling products. When multiple customers attempt to purchase the same item simultaneously, the system must ensure that stock levels are accurately maintained and never go below zero. This is critical for maintaining data integrity and preventing negative inventory scenarios that could lead to business losses.

## Requirements

1. The system must atomically check current stock levels and decrement inventory in a single operation
2. Stock updates must prevent race conditions when multiple concurrent requests attempt to modify the same product's inventory
3. The system must reject purchase attempts when insufficient stock is available
4. Stock levels must never be allowed to go below zero under any circumstances
5. The system must handle concurrent access to the same product inventory without data corruption
6. All stock operations must be transactionally safe and rollback on failure
7. The system must provide clear feedback when stock is insufficient for a requested quantity
8. Stock checks and updates must be performed as close together as possible to minimize timing windows

## Constraints

- Stock quantities must be non-negative integers
- The system must handle high-concurrency scenarios with multiple simultaneous users
- Database operations must maintain ACID properties for inventory transactions
- Stock updates must be idempotent where possible
- The system must gracefully handle database connection failures during stock operations
- Performance must remain acceptable under concurrent load

## References

See context.md for existing codebase structure and related inventory management implementations.