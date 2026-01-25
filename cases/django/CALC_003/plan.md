# Floating Point Currency Price Calculator

## Overview

This Django application component handles price calculations for e-commerce transactions where monetary values must be processed with exact decimal precision. The system needs to calculate final prices including tax, discounts, and other adjustments while maintaining financial accuracy required for currency operations.

## Requirements

1. Create a Django model to represent a product with a base price stored as a decimal field
2. Implement a method to calculate the final price including a percentage-based tax rate
3. Support applying a fixed discount amount to the calculated price
4. Ensure all monetary calculations preserve decimal precision to at least 2 decimal places
5. Handle tax rates provided as percentages (e.g., 8.25 for 8.25% tax)
6. Return the final calculated price as a properly formatted decimal value
7. Validate that base prices are non-negative values
8. Validate that tax rates are non-negative percentages
9. Ensure discount amounts do not exceed the pre-discount total
10. Provide a string representation method that displays the final price in standard currency format

## Constraints

- Base prices must be greater than or equal to zero
- Tax rates must be non-negative and represent percentages
- Discount amounts cannot result in negative final prices
- All monetary values must maintain precision suitable for currency operations
- The system must handle edge cases where discounts equal or exceed the pre-discount total
- Price calculations must be deterministic and repeatable

## References

See context.md for existing Django model patterns and decimal field implementations used in the codebase.