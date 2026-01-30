# Order Total Calculation with Consistent Rounding

## Overview

The system needs to calculate order totals for e-commerce transactions with proper financial precision. Order totals are computed from line items (quantity × unit price) plus applicable taxes. All monetary calculations must use consistent rounding rules to ensure accurate financial reporting and prevent discrepancies in accounting records.

## Requirements

1. Calculate line item subtotals by multiplying quantity by unit price
2. Sum all line item subtotals to get the order subtotal
3. Calculate tax amount by applying the tax rate to the order subtotal
4. Calculate final order total by adding order subtotal and tax amount
5. Apply consistent rounding to 2 decimal places for all monetary values
6. Use banker's rounding (round half to even) for all financial calculations
7. Return the final order total as a BigDecimal with 2 decimal places
8. Handle orders with multiple line items of varying quantities and prices
9. Support tax rates expressed as decimal percentages (e.g., 0.08 for 8%)
10. Ensure intermediate calculations maintain precision before final rounding

## Constraints

1. All monetary amounts must be represented using BigDecimal for precision
2. Quantities must be positive integers
3. Unit prices must be positive monetary values
4. Tax rates must be non-negative decimal values
5. The system must handle edge cases where rounding affects the final penny
6. All calculations must be deterministic and repeatable
7. Input validation should reject null or invalid values

## References

See context.md for existing order processing implementations and related financial calculation patterns.