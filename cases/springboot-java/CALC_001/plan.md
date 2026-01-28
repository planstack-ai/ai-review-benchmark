# Member Discount Rate Calculation Service

## Overview

This service implements a discount calculation system for an e-commerce platform that provides preferential pricing to registered members. The system needs to differentiate between regular customers and members, applying appropriate discount rates to calculate final pricing for orders.

## Requirements

1. Create a discount calculation service that accepts customer type and order amount as inputs
2. Apply a 10% discount rate for customers identified as "members"
3. Apply no discount (0%) for customers who are not members
4. Return the discounted amount as the final calculation result
5. Handle decimal precision appropriately for monetary calculations
6. Provide clear method signatures that indicate the discount calculation purpose
7. Implement proper input validation for order amounts
8. Support both member and non-member customer types through a clear classification system

## Constraints

1. Order amounts must be positive values greater than zero
2. Discount rates must be expressed as percentages (10% = 0.10 in decimal form)
3. Final calculated amounts should maintain appropriate decimal precision for currency
4. Customer type classification must be case-insensitive
5. The service should handle null or invalid inputs gracefully
6. Discount application should only occur for valid member classifications

## References

See context.md for existing service patterns and integration requirements within the Spring Boot application structure.