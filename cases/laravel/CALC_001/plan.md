# Member Discount Rate Calculation System

## Overview

The system needs to calculate discounted prices for customers based on their membership status. Members receive a 10% discount on their purchases, while non-members pay the full price. This feature is essential for the e-commerce platform's pricing strategy and customer retention program.

## Requirements

1. The system must identify whether a customer has member status
2. Members must receive exactly 10% discount on their total purchase amount
3. Non-members must pay the full price without any discount
4. The discount calculation must preserve the original price for audit purposes
5. The system must return both the original price and the final discounted price
6. The discount amount must be calculated and stored separately
7. All monetary calculations must handle decimal precision appropriately
8. The system must handle zero and negative price inputs gracefully

## Constraints

1. Discount percentage is fixed at 10% and cannot be modified by users
2. Member status must be explicitly verified before applying discount
3. Price inputs must be numeric values
4. Discounted prices must not result in negative values
5. The system must maintain calculation accuracy to at least 2 decimal places
6. Member status determination must be boolean (true/false)

## References

See context.md for existing discount calculation patterns and member verification implementations used elsewhere in the codebase.
