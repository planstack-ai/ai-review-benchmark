# Tax Calculation Order Service

## Overview

This service handles tax calculations for e-commerce orders, applying discounts before calculating tax amounts. The system must ensure proper order of operations when processing financial calculations to maintain accuracy and compliance with tax regulations.

## Requirements

1. Calculate the subtotal from item prices and quantities
2. Apply discount amount to the subtotal to get the discounted total
3. Calculate tax as 10% of the discounted total (after discount is applied)
4. Return the final total including the calculated tax amount
5. Accept input parameters for items (price and quantity), discount amount, and return calculated totals
6. Provide separate values for subtotal, discount applied, tax amount, and final total
7. Handle decimal precision appropriately for monetary calculations
8. Process multiple items in a single order calculation

## Constraints

1. Tax rate is fixed at 10% and cannot be modified
2. Discount must be applied before tax calculation, never after
3. All monetary values must be handled with appropriate decimal precision
4. Negative discounts are not allowed
5. Item quantities must be positive integers
6. Item prices must be positive values
7. The service must return structured data containing all calculation components

## References

See context.md for existing service patterns and architectural guidelines within the Spring Boot application structure.