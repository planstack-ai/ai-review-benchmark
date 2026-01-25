# Stock Allocation Service

## Overview

The system manages stock allocation for an e-commerce cart. It handles adding items to cart, removing items, and processing checkout with stock reservations.

## Requirements

1. Add items to cart with stock validation
2. Reserve stock when items are added to cart
3. Release reserved stock when items are removed
4. Process checkout and convert reservations to actual sales
5. Handle stock reservation expiration
6. **Stock should be reserved at checkout, not at cart addition**

## Constraints

1. Stock reservations should be temporary
2. Cart abandonment should release reserved stock
3. Stock reservation at cart time causes stock lockup issues
4. Only reserve stock at payment confirmation

## References

See context.md for stock reservation model and timing requirements.
