# Stock Allocation Timing for E-commerce Inventory Management

## Overview

This feature implements proper stock allocation timing for an e-commerce inventory system. The business requirement is to reserve inventory only when customers proceed to checkout, not when items are added to their shopping cart. This approach prevents inventory from being unnecessarily tied up by items sitting in abandoned carts while still ensuring stock availability during the critical checkout process.

## Requirements

1. Stock must NOT be reserved or allocated when items are added to the shopping cart
2. Stock reservation must occur only when the checkout process is initiated
3. Reserved stock must be released if the checkout process is abandoned or times out
4. The system must check actual available stock (not reserved stock) when displaying product availability
5. Stock allocation must be atomic to prevent race conditions during concurrent checkouts
6. Reserved stock must be committed (permanently allocated) only upon successful payment completion
7. The system must handle cases where stock becomes unavailable between cart addition and checkout
8. Stock reservation must include a timeout mechanism to automatically release expired reservations
9. Users must receive clear feedback when items in their cart become unavailable at checkout
10. The system must maintain accurate stock levels by distinguishing between available, reserved, and allocated stock

## Constraints

1. Stock levels cannot go below zero for available inventory
2. Reserved stock must have an expiration time (maximum 15 minutes from checkout initiation)
3. Only authenticated users can proceed to checkout and trigger stock reservation
4. Stock reservation must fail gracefully if insufficient inventory is available
5. The system must handle concurrent checkout attempts for the same product
6. Reserved stock that expires must be automatically returned to available inventory
7. Stock allocation changes must be logged for audit purposes

## References

See context.md for existing cart, product, and order model implementations that this feature should integrate with.