# Tax Calculation Order System

## Overview

This system implements a tax calculation feature for an e-commerce platform where customers receive discounts on their purchases and tax is applied to the final discounted amount. The business requirement is to ensure proper order of operations: apply discount first, then calculate tax on the discounted total to provide accurate pricing for customers.

## Requirements

1. Create a Django model to represent an order with base amount and discount percentage fields
2. Implement a method to calculate the discounted amount by applying the discount percentage to the base amount
3. Implement a method to calculate tax at 10% rate on the discounted amount
4. Implement a method to calculate the final total by adding tax to the discounted amount
5. Ensure all monetary calculations return values rounded to 2 decimal places
6. The discount should be applied as a percentage reduction (e.g., 20% discount means customer pays 80% of original price)
7. Tax calculation must occur after discount application, not on the original base amount

## Constraints

1. Base amount must be a positive decimal value
2. Discount percentage must be between 0 and 100 (inclusive)
3. Tax rate is fixed at 10% and should not be configurable
4. All monetary values should be handled as Decimal type for precision
5. Methods should handle edge cases where discount is 0% or 100%

## References

See context.md for existing model structures and calculation patterns used in the codebase.