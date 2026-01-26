# Inventory Reserved vs Available Stock Tracking System

## Overview

The inventory management system needs to distinguish between reserved stock (items allocated to pending orders but not yet shipped) and available stock (items that can be allocated to new orders). This separation is critical for accurate inventory reporting and preventing overselling scenarios where the system shows items as available when they are already committed to existing orders.

## Requirements

1. The system must track total stock quantity for each inventory item
2. The system must track reserved stock quantity separately from total stock
3. Available stock must be calculated as the difference between total stock and reserved stock
4. When an order is created, the required quantity must be reserved from available stock
5. Reserved stock must be decremented when an order is shipped or fulfilled
6. Reserved stock must be released back to available stock when an order is cancelled
7. The system must prevent reserving more stock than is currently available
8. Stock reservation operations must be atomic to prevent race conditions
9. The system must provide methods to query both reserved and available quantities
10. Stock levels must never become negative for either total or reserved quantities

## Constraints

1. Reserved stock quantity cannot exceed total stock quantity at any time
2. Available stock calculation must always return a non-negative value
3. Stock reservation must fail if insufficient available stock exists
4. All stock operations must maintain data consistency across concurrent requests
5. The system must handle edge cases where reserved stock equals total stock (zero availability)
6. Stock adjustments must properly update both total and reserved quantities as appropriate

## References

See context.md for existing inventory model implementations and related order management functionality.