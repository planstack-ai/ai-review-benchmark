# Points Calculation Service

## Overview

This service implements a loyalty points calculation system for an e-commerce platform. When customers complete purchases, they earn points based on their payment amount. The points can be redeemed for future discounts.

## Requirements

1. Create a points calculation service that calculates reward points based on order payment
2. Award points at a rate of 1 point per 100 yen spent
3. Points should be calculated based on the actual payment amount after all discounts are applied
4. Support for orders with multiple discount types (member discount, coupon discount)
5. Handle decimal precision appropriately for point calculations
6. Round down fractional points (e.g., 1050 yen = 10 points, not 11)
7. Provide clear method signatures for point calculation
8. Log point awards for auditing purposes

## Constraints

1. Order amounts must be positive values
2. Point rate must be configurable but defaults to 1 point per 100 yen
3. Points must be whole numbers (no fractional points)
4. Discounts must be applied before point calculation
5. The service should be stateless and thread-safe
6. Maximum points per transaction is 10,000

## References

See context.md for existing points calculation patterns and service implementations in the codebase.
