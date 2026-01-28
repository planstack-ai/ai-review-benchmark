# Pricing Calculation Service

## Overview

This service provides precise currency calculations for e-commerce pricing operations including subtotals, discounts, taxes, and processing fees. The system must handle all monetary values with exact decimal precision using BigDecimal to ensure accurate financial transactions and prevent floating-point rounding errors.

## Requirements

1. Calculate total price from a list of price items with customer tier-based discounts
2. Calculate subtotal by summing item prices (unit price × quantity)
3. Apply discount based on customer tier (PREMIUM: 15%, STANDARD: 10%) when subtotal exceeds threshold
4. Calculate tax on the discounted price using the configured tax rate
5. Calculate processing fee as a percentage of the discounted amount
6. Provide a price breakdown showing subtotal, discount, tax, processing fee, and total
7. Support bulk discount calculation for large quantity orders
8. All monetary calculations must use BigDecimal to avoid floating-point precision errors
9. Round final amounts to 2 decimal places using HALF_UP rounding

## Constraints

1. All monetary values must be represented using BigDecimal for precision
2. NEVER use double or float for monetary calculations - this causes precision errors
3. Processing fee rate calculations must also use BigDecimal, not primitive doubles
4. Discount threshold is $100.00
5. Tax rate is 8%
6. All intermediate and final calculations must maintain decimal precision

## References

See context.md for existing pricing patterns and BigDecimal usage examples.