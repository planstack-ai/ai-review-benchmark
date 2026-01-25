# Price Calculation with Discount Codes

## Overview

The system needs to calculate product prices with various discounts applied. It handles bulk discounts for orders over a threshold and promotional discount codes. The calculation must be precise for monetary values to ensure accurate pricing.

## Requirements

1. Calculate the base subtotal from unit price and quantity
2. Apply bulk discount (5%) when order exceeds $100 threshold
3. Apply promotional discount codes (SAVE10=10%, WELCOME5=5%, STUDENT15=15%)
4. Calculate tax at 8% on the discounted amount
5. Return both individual breakdown and final total
6. Handle multiple discount types that can stack
7. Validate discount codes against allowed list
8. Round final amounts to 2 decimal places

## Constraints

1. Base price must be positive
2. Quantity must be positive integer
3. Discount codes are case-insensitive
4. Only one promotional code can be used per order
5. Bulk discount always applies if threshold met
6. Tax rate is fixed at 8%
7. All monetary calculations must handle decimal precision

## References

See context.md for existing pricing patterns and discount code validation implementations.
