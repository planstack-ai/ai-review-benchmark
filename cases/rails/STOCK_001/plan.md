# Stock Allocation Timing for E-commerce Inventory Management

## Overview

This feature implements proper stock allocation timing for an e-commerce platform's inventory management system. The core business requirement is to reserve inventory at the point of checkout initiation rather than when items are added to the shopping cart. This approach prevents inventory from being unnecessarily tied up by abandoned carts while ensuring stock availability during the actual purchase process.

## Requirements

1. Stock must NOT be reserved when items are added to a shopping cart
2. Stock reservation must occur when the checkout process is initiated
3. Reserved stock must be released if checkout is not completed within a specified timeout period
4. The system must handle concurrent checkout attempts for the same product gracefully
5. Stock levels must accurately reflect available inventory minus reserved quantities
6. Users must receive clear feedback when attempting to checkout items that are no longer available
7. The reservation system must track which user has reserved specific stock quantities
8. Reserved stock must be automatically converted to allocated stock upon successful payment completion
9. The system must prevent overselling by validating stock availability at reservation time
10. Stock reservations must be released immediately upon checkout cancellation or failure

## Constraints

1. Stock reservations must expire after 15 minutes of inactivity during checkout
2. A single user cannot reserve more stock than is currently available
3. Stock levels cannot go below zero at any point in the process
4. The system must handle race conditions when multiple users attempt to reserve the last available units
5. Reserved stock quantities must be whole numbers (no fractional reservations)
6. Users must complete checkout within the reservation timeout period
7. The system must maintain data consistency even during high-concurrency scenarios

## References

See context.md for existing cart, checkout, and inventory model implementations that this feature should integrate with.