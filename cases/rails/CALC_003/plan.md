# Order Total Calculation with Consistent Rounding

## Overview

The system needs to calculate order totals for e-commerce transactions. Orders contain multiple line items, each with a quantity and unit price. The system must apply tax calculations and ensure consistent rounding behavior across all monetary calculations to maintain financial accuracy and compliance with accounting standards.

## Requirements

1. Calculate the subtotal by multiplying quantity and unit price for each line item
2. Sum all line item subtotals to get the order subtotal
3. Calculate tax amount by applying the tax rate to the order subtotal
4. Calculate the final order total by adding the order subtotal and tax amount
5. Round all monetary values to exactly 2 decimal places using banker's rounding (round half to even)
6. Apply rounding consistently at each calculation step, not just the final result
7. Handle orders with zero, one, or multiple line items
8. Support tax rates expressed as decimal percentages (e.g., 0.08 for 8%)

## Constraints

1. All monetary amounts must be positive or zero
2. Quantities must be positive integers
3. Tax rates must be between 0.0 and 1.0 (inclusive)
4. Unit prices must be positive decimal values
5. The system must handle edge cases where intermediate calculations result in values requiring rounding
6. All calculations must maintain precision throughout the computation chain

## References

See context.md for existing system architecture and related financial calculation patterns used in the codebase.