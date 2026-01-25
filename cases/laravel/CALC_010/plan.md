# Bulk Order Calculation System

## Overview

The system calculates totals for bulk orders with potentially large quantities and high-value items. It applies percentage discounts, bulk discount multipliers, and tax calculations. The system must handle large numbers accurately to prevent overflow issues.

## Requirements

1. Calculate subtotal from unit price and quantity for each item
2. Apply percentage discount to subtotal
3. Apply 15% additional bulk discount when eligible (100+ items or $10,000+ subtotal)
4. Calculate tax at configurable rate on discounted amount
5. Return formatted result with all breakdown values
6. Validate item data (positive prices and quantities)
7. Support both hash and array item formats
8. **Handle large quantities without integer overflow**
9. Format currency values to 2 decimal places

## Constraints

1. Discount percentage must be between 0 and 100
2. Order must have at least one item
3. Unit prices must be positive numbers
4. Quantities must be positive integers
5. Tax rate defaults to 8% if not specified
6. **Use arbitrary precision arithmetic for large calculations**
7. Bulk discount eligibility check runs before discount calculation

## References

See context.md for bulk discount rules and expected calculation precision requirements.
