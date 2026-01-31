# Multi-Step Price Calculation System

## Overview

This system implements a comprehensive pricing engine for an e-commerce platform that applies multiple discount types and tax calculations in a specific order. The system must handle quantity-based discounts, customer-specific discounts, promotional campaigns, and tax calculations while maintaining accurate financial records and providing transparent pricing breakdowns to customers.

## Requirements

1. Calculate base price by multiplying item unit price by quantity
2. Apply quantity discount based on volume tiers (e.g., 5% for 10+ items, 10% for 50+ items)
3. Apply customer-specific discount percentage based on customer loyalty level or membership status
4. Apply promotional discount codes that can be either percentage-based or fixed amount
5. Calculate tax on the discounted subtotal using the applicable tax rate
6. Return a detailed breakdown showing each calculation step and the final total
7. Support multiple currency formats and round all monetary values to 2 decimal places
8. Validate that all discount percentages are between 0 and 100
9. Ensure promotional discount codes are active and not expired
10. Handle cases where promotional discounts cannot exceed the current subtotal
11. Log all pricing calculations for audit purposes
12. Provide clear error messages for invalid inputs or expired promotions

## Constraints

- Quantity must be a positive integer greater than 0
- Unit price must be a positive decimal value
- Discount percentages must be between 0 and 100 inclusive
- Tax rates must be between 0 and 50 inclusive
- Promotional codes must have valid start and end dates
- Fixed amount promotional discounts cannot exceed the current subtotal
- All monetary calculations must maintain precision to avoid rounding errors
- Customer discount and promotional discount cannot both exceed 90% combined
- System must handle edge cases where subtotal becomes zero or negative

## References

See context.md for existing implementation patterns and database schema requirements.