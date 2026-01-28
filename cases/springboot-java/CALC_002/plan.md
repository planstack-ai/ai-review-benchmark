# Tax Calculation Order Service

## Overview

This service implements a tax calculation system for e-commerce orders that applies discounts before calculating taxes. The business requirement is to ensure customers receive the benefit of tax calculations on the already-discounted price, which is a common practice in retail to provide better customer value and comply with standard accounting practices.

## Requirements

1. Create a service class that calculates the total amount for an order
2. Apply any discount amount to the original price first
3. Calculate 10% tax on the discounted price (not the original price)
4. Return the final total as discounted price plus tax
5. Accept three parameters: original price, discount amount, and tax rate
6. Use BigDecimal for all monetary calculations to ensure precision
7. The tax rate should be configurable but default to 10% (0.10)
8. Return the calculated total with proper decimal precision

## Constraints

1. Original price must be greater than zero
2. Discount amount cannot be negative
3. Discount amount cannot exceed the original price
4. Tax rate must be between 0 and 1 (representing 0% to 100%)
5. All monetary values should be rounded to 2 decimal places
6. Throw appropriate exceptions for invalid input parameters

## References

See context.md for examples of existing calculation services and standard patterns used in the codebase.