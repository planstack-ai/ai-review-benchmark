# Bulk Order Total Calculation System

## Overview

The system needs to handle bulk order calculations for e-commerce scenarios where customers can purchase large quantities of items. The application must accurately calculate order totals while handling various quantity scenarios, including edge cases where quantities might exceed normal ranges or cause computational issues.

## Requirements

1. Calculate the total cost for an order by multiplying item price by quantity
2. Support quantity values up to 1,000,000 units per item
3. Handle decimal prices with up to 2 decimal places precision
4. Return the total as a decimal value with proper precision
5. Process multiple items in a single order calculation
6. Validate that quantity values are positive integers
7. Validate that price values are positive numbers
8. Raise appropriate exceptions for invalid input data
9. Maintain calculation accuracy for large quantity orders
10. Support bulk discount calculations when quantity exceeds threshold values

## Constraints

1. Quantity must be a positive integer greater than 0
2. Price must be a positive decimal value greater than 0
3. Maximum quantity per item is 1,000,000 units
4. Price precision must not exceed 2 decimal places
5. Total calculation must maintain decimal precision throughout the process
6. System must handle edge cases where calculations might result in very large numbers
7. Input validation must occur before any calculations are performed
8. All monetary values must use appropriate decimal types to avoid floating-point errors

## References

See context.md for existing Django model implementations and related calculation utilities that should be leveraged in this implementation.