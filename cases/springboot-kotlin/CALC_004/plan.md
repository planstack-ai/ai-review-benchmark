# Order Total Calculation with Consistent Rounding

## Overview

The system needs to calculate order totals for e-commerce transactions. Each order contains multiple line items with quantities and unit prices. The business requires consistent rounding behavior across all calculations to ensure accurate financial reporting and customer billing. All monetary calculations must follow standardized rounding rules to prevent discrepancies in accounting and customer charges.

## Requirements

1. Calculate the subtotal for each line item by multiplying quantity by unit price
2. Apply consistent rounding to two decimal places for all monetary calculations
3. Sum all line item subtotals to produce the final order total
4. Use banker's rounding (round half to even) for all rounding operations
5. Return the order total as a BigDecimal with exactly two decimal places
6. Handle orders with zero line items by returning zero total
7. Validate that all input prices are non-negative
8. Validate that all quantities are positive integers

## Constraints

- Unit prices must be non-negative BigDecimal values
- Quantities must be positive integers (greater than zero)
- All monetary values must be rounded to exactly two decimal places
- Empty orders (no line items) are valid and should return 0.00
- Maximum of 1000 line items per order
- Unit prices cannot exceed 999,999.99

## References

See context.md for existing implementation patterns and related code examples in the codebase.