# Points Calculation Order System

## Overview

The system needs to calculate customer reward points based on their payment amounts. Points should be awarded after applying any applicable discounts to ensure customers earn points only on the actual amount they pay, not on the original price before discounts.

## Requirements

1. Calculate points based on the final payment amount after all discounts have been applied
2. Apply a standard points multiplier to determine the total points earned
3. Process discount calculations before points calculations in the workflow
4. Store both the original amount and discounted amount for audit purposes
5. Award points only for completed transactions
6. Round points calculations to the nearest whole number
7. Ensure points calculations are performed in the correct sequence relative to other transaction processing steps

## Constraints

1. Points cannot be negative values
2. Discount amounts cannot exceed the original transaction amount
3. Points calculation must occur after payment validation
4. Zero-amount transactions should not award points
5. Refunded transactions should deduct previously awarded points

## References

See context.md for existing payment processing and discount calculation implementations that this points system must integrate with.