# Order Total Calculation with Consistent Rounding

## Overview

The system needs to calculate order totals for e-commerce transactions with proper financial precision. Order totals are computed from line items (quantity × unit price) plus applicable taxes and fees. All monetary calculations must use consistent rounding rules to ensure accurate financial reporting and prevent discrepancies in accounting records.

## Requirements

1. Calculate line item subtotals by multiplying quantity by unit price
2. Sum all line item subtotals to get the order subtotal
3. Apply tax rate to the order subtotal to calculate tax amount
4. Add any additional fees to the calculation
5. Sum subtotal, tax amount, and fees to get the final order total
6. Round all monetary values to 2 decimal places using banker's rounding (round half to even)
7. Apply rounding consistently at each calculation step, not just the final result
8. Return the order total as a Decimal type with 2 decimal places
9. Handle orders with zero or negative quantities appropriately
10. Preserve calculation precision throughout the entire process

## Constraints

- All monetary values must be represented as Decimal types for precision
- Tax rates are provided as decimal percentages (e.g., 0.08 for 8%)
- Unit prices and fees are already provided with appropriate decimal precision
- Quantities must be positive integers greater than zero
- The system must handle edge cases where intermediate calculations result in values requiring rounding
- All rounding must follow the same rule throughout the calculation process

## References

See context.md for existing model structures and related implementations in the codebase.