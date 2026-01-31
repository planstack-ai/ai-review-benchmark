# Free Shipping Boundary Calculation Service

## Overview

This service determines whether an order qualifies for free shipping based on the order total amount. The business offers free shipping as an incentive for customers to reach a minimum purchase threshold, helping to increase average order value while providing customer benefits.

## Requirements

1. The service must calculate free shipping eligibility for orders with a total of 5000 yen or more
2. Orders with totals below 5000 yen must not qualify for free shipping
3. The service must accept order total amounts as numeric input
4. The service must return a boolean result indicating free shipping eligibility
5. The calculation must use the exact threshold of 5000 yen (inclusive)
6. The service must be implemented as a Spring Boot service component
7. The service must handle the 5000 yen boundary case correctly (exactly 5000 yen qualifies)

## Constraints

1. Order total amounts must be non-negative values
2. Zero or negative order amounts should not qualify for free shipping
3. The service should handle decimal amounts appropriately
4. Currency is assumed to be Japanese Yen (JPY)
5. No rounding or currency conversion is required

## References

See context.md for existing service patterns and architectural guidelines within the codebase.