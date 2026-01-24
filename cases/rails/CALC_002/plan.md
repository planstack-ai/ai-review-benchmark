# Tax Calculation Order System

## Overview

This system implements a tax calculation feature for an e-commerce platform where customers receive discounts on their purchases and tax is applied to the final amount. The business requirement is to ensure proper order of operations: discounts are applied first to reduce the subtotal, then tax is calculated on the discounted amount to determine the final total.

## Requirements

1. The system must accept a subtotal amount as input
2. The system must accept a discount percentage as input (0-100)
3. The system must apply the discount percentage to the subtotal to calculate a discounted amount
4. The system must apply a fixed 10% tax rate to the discounted amount
5. The system must return the final total including tax
6. The calculation order must be: subtotal → apply discount → apply tax → final total
7. All monetary calculations must preserve precision to 2 decimal places
8. The system must handle zero discount scenarios (0% discount)
9. The system must handle maximum discount scenarios (100% discount)

## Constraints

1. Subtotal must be a positive number greater than 0
2. Discount percentage must be between 0 and 100 (inclusive)
3. Tax rate is fixed at 10% and cannot be modified
4. Input validation must reject negative subtotals
5. Input validation must reject discount percentages outside the 0-100 range
6. The system must raise appropriate errors for invalid inputs
7. Monetary amounts must be rounded to 2 decimal places using standard rounding rules

## References

See context.md for existing tax calculation implementations and related business logic patterns used throughout the application.