# Inventory Reserved Stock Tracking System

## Overview

The inventory system needs to maintain separate tracking of reserved and available stock quantities to prevent overselling and ensure accurate inventory management. When items are reserved (e.g., in shopping carts, pending orders), they should be deducted from available stock while maintaining the total physical stock count. This separation allows the system to distinguish between items that are physically present but committed to customers versus items that are truly available for new orders.

## Requirements

1. The system shall track total physical stock quantity for each inventory item
2. The system shall track reserved stock quantity separately from total stock
3. The system shall calculate available stock as the difference between total stock and reserved stock
4. When stock is reserved, the reserved quantity shall increase while total stock remains unchanged
5. When reserved stock is released (order cancelled, cart abandoned), the reserved quantity shall decrease
6. When reserved stock is fulfilled (order completed), both total stock and reserved stock shall decrease by the same amount
7. The available stock calculation shall always reflect the current reservable quantity
8. Stock reservation operations shall be atomic to prevent race conditions
9. The system shall prevent reserving more stock than is currently available
10. All stock quantities shall be non-negative integers

## Constraints

1. Reserved stock quantity cannot exceed total stock quantity at any time
2. Available stock cannot be negative - reservation requests exceeding available stock must be rejected
3. Stock adjustments must maintain data consistency across all related quantities
4. Concurrent reservation attempts for the same item must be handled safely
5. Reserved stock that remains unreleased for extended periods should be identifiable for cleanup processes

## References

See context.md for existing inventory management patterns and database schema considerations.