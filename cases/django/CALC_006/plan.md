# Free Shipping Boundary Calculation

## Overview

This feature implements a free shipping threshold system for an e-commerce platform. When customers reach a minimum order value of 5000 yen, they qualify for free shipping. This encourages larger orders and improves customer satisfaction by removing shipping costs for substantial purchases.

## Requirements

1. Calculate whether an order qualifies for free shipping based on a 5000 yen threshold
2. Accept order total as input parameter in yen currency
3. Return a boolean value indicating free shipping eligibility
4. Apply the threshold inclusively (orders of exactly 5000 yen qualify)
5. Handle decimal values in order totals appropriately
6. Provide clear function naming that indicates free shipping calculation
7. Include appropriate input validation for the order total parameter
8. Support integration with Django's decimal handling for currency values

## Constraints

1. Order total must be a positive numeric value
2. Zero or negative order totals should not qualify for free shipping
3. The 5000 yen threshold is fixed and should not be configurable within this function
4. Function should handle both integer and decimal input values
5. Invalid input types should be handled gracefully
6. Currency conversion is not required - assume all inputs are in yen

## References

See context.md for existing codebase patterns and Django project structure.