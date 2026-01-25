# Shipping Fee Calculation System

## Overview

The system calculates shipping fees for e-commerce orders based on shipping method, order total, and weight. Standard shipping is free for domestic orders that meet the minimum threshold. Express shipping has additional weight-based fees for heavy orders.

## Requirements

1. Standard shipping fee is 500 yen
2. Express shipping fee is 800 yen base
3. Free shipping for standard method when order total is 5000 yen or more
4. Free shipping only applies to domestic (Japan) orders
5. Add weight surcharge for express shipping on orders over 10kg
6. Weight surcharge is 100 yen per additional 1kg (rounded up)
7. Order total includes subtotal plus tax minus discounts
8. Return 0 for free shipping eligible orders

## Constraints

1. Free shipping threshold is exactly 5000 yen (inclusive)
2. International orders never qualify for free shipping
3. Express shipping always has a fee (no free express shipping)
4. Weight is measured in grams
5. Default to standard shipping if method not specified
6. Heavy order threshold is 10,000 grams (10kg)

## References

See context.md for shipping address model and product weight definitions.
