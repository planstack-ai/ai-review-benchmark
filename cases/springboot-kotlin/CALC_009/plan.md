# Minimum Order Validation Service

## Overview

This service implements order validation logic for an e-commerce platform. The system enforces a minimum order amount policy to ensure orders meet business requirements before processing.

## Requirements

1. Create an order validation service that checks minimum order amount requirements
2. Minimum order amount is 1000 yen after all discounts are applied
3. Validate orders before payment processing
4. Return clear error messages when minimum is not met
5. Calculate the remaining amount needed to meet minimum
6. Support different minimum amounts for different order types
7. Handle decimal precision appropriately
8. Log validation failures for analytics

## Constraints

1. Minimum order check must be performed after all discounts are applied
2. Minimum amount must be configurable
3. Validation must occur before payment processing
4. Gift cards and promotional items may have different rules
5. The service should be stateless and thread-safe
6. Free shipping thresholds are separate from minimum order amount

## References

See context.md for existing order validation patterns and service implementations in the codebase.
