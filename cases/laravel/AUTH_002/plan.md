# Cart Manipulation Authorization System

## Overview

The system manages shopping cart operations for an e-commerce platform. Users can add, remove, update, and clear items in their carts. Each cart belongs to a specific user, and operations must be restricted to the cart owner only.

## Requirements

1. Users must be authenticated to perform cart operations
2. Users can only manipulate their own cart
3. Support add, remove, update, and clear operations
4. Validate item existence before adding to cart
5. Track total items and total amount after each operation
6. Handle quantity updates for existing items
7. Return appropriate error messages for invalid operations

## Constraints

1. Cart ID should not be directly accessible via user input
2. Only the cart owner should be able to modify the cart
3. Item quantities must be positive integers
4. Cart should be accessed through user relationship

## References

See context.md for Cart and CartItem model relationships.
