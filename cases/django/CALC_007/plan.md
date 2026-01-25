# Points Calculation System for E-commerce Orders

## Overview

The system needs to calculate loyalty points for customer orders based on the final payment amount after all discounts have been applied. This ensures customers earn points only on the actual amount they pay, not on the original order total before discounts.

## Requirements

1. Calculate points based on the payment amount after discount deduction
2. Use a configurable points-to-currency ratio for the calculation
3. Round down the calculated points to the nearest whole number
4. Store the calculated points in the order record
5. Ensure points calculation occurs after discount processing
6. Handle cases where discount amount equals or exceeds the order total
7. Return the calculated points value from the calculation method
8. Validate that the payment amount is non-negative before calculation

## Constraints

1. Points cannot be negative - minimum value is 0
2. Discount amount cannot exceed the original order total
3. Payment amount must be calculated as: order total minus discount amount
4. Points calculation must only occur for completed payment processing
5. The points-to-currency ratio must be a positive number
6. All monetary calculations should maintain precision until final rounding

## References

See context.md for existing order processing workflow and related model implementations.