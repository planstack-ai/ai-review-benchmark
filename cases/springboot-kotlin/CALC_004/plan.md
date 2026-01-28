# Order Total Calculation with Consistent Rounding

## Overview

The system needs to calculate order totals for e-commerce transactions with proper financial precision. Order totals are computed from line items (quantity × unit price) plus applicable taxes, discounts, and shipping. All monetary calculations must use consistent rounding rules to ensure accurate financial reporting.

## Requirements

1. Calculate line item subtotals by multiplying quantity by unit price
2. Sum all line item subtotals to get the order subtotal
3. Apply discounts and calculate tax on the discounted amount
4. Add shipping costs to get the final order total
5. Apply rounding to 2 decimal places using HALF_UP mode
6. IMPORTANT: Round the FINAL sum, not individual items before summing
   - Correct: Sum all item subtotals first, then round the total once
   - Wrong: Round each item subtotal individually, then sum (causes penny discrepancies)
7. Return the final order total as a BigDecimal with 2 decimal places
8. Handle orders with multiple line items of varying quantities and prices

## Constraints

1. All monetary amounts must be represented using BigDecimal for precision
2. Quantities must be positive integers
3. Unit prices must be positive monetary values
4. Rounding must happen AFTER summing, not before (to avoid cumulative rounding errors)
5. The system must handle edge cases where rounding order affects the final amount
6. All calculations must be deterministic and repeatable

## References

See context.md for existing order processing implementations and related financial calculation patterns.