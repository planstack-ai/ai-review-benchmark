# Multi-Step Price Calculation System

## Overview

This system implements a comprehensive pricing engine that calculates final product prices through multiple sequential steps. The business requires accurate price computation that accounts for base pricing, quantity-based discounts, tax calculations, and promotional adjustments. The system must handle various product types and customer segments while maintaining precision in financial calculations.

## Requirements

1. Calculate base price from product unit price and quantity
2. Apply quantity-based discount tiers (bulk pricing discounts)
3. Calculate subtotal after quantity discounts
4. Apply customer segment discounts (premium, standard, basic customer types)
5. Calculate tax amount based on applicable tax rate
6. Apply promotional discounts to pre-tax amount
7. Calculate final total price including all adjustments
8. Return detailed price breakdown showing each calculation step
9. Handle decimal precision to 2 decimal places for all monetary values
10. Support multiple currency formats in price display
11. Process discount percentages as decimal values (0.0 to 1.0 range)
12. Maintain calculation order: quantity discount → customer discount → tax → promotional discount

## Constraints

1. Quantity must be positive integer greater than zero
2. Unit price must be positive decimal value
3. Discount percentages must be between 0.0 and 1.0 inclusive
4. Tax rates must be non-negative decimal values
5. All monetary calculations must round to 2 decimal places using banker's rounding
6. Customer segment must be one of: premium, standard, basic
7. Promotional discounts cannot exceed 50% of pre-tax amount
8. Minimum order total after all discounts must be greater than zero
9. Maximum quantity per order is 10,000 units
10. Tax calculation must occur before promotional discount application

## References

See context.md for existing pricing calculation patterns and business rule implementations used throughout the application.