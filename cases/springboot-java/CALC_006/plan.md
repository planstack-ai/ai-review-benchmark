# Free Shipping Boundary Calculation Service

## Overview

This service determines whether an order qualifies for free shipping based on the order total amount. The business rule is designed to encourage larger purchases by offering free shipping as an incentive for customers who meet the minimum order threshold.

## Requirements

1. The service must accept an order total amount as input
2. The service must return a boolean value indicating whether the order qualifies for free shipping
3. Orders with a total of 5000 yen or more must qualify for free shipping
4. Orders with a total less than 5000 yen must not qualify for free shipping
5. The service must handle the exact boundary value of 5000 yen correctly
6. The service must be implemented as a Spring Boot component or service
7. The calculation logic must be encapsulated in a dedicated method
8. The service must handle numeric input appropriately for currency calculations

## Constraints

1. Input amounts must be non-negative values
2. The service should handle null input gracefully
3. Currency precision must be maintained throughout the calculation
4. The 5000 yen threshold is inclusive (5000 yen qualifies for free shipping)
5. Input validation should prevent invalid order amounts

## References

See context.md for existing service patterns and Spring Boot configuration examples in the codebase.