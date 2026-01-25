# Tax Calculation Service Implementation

## Overview

The system requires a tax calculation service that applies the current standard tax rate to product prices. This service will be used across the e-commerce platform to ensure consistent tax calculations for order processing, price displays, and financial reporting. The tax rate is currently set at 10% and should be applied uniformly to all taxable items.

## Requirements

1. Create a tax calculation service that accepts a base price as input
2. Apply a 10% tax rate to the provided base price
3. Return the calculated tax amount as a decimal value
4. Ensure the service handles both integer and decimal price inputs
5. Round tax calculations to 2 decimal places for currency precision
6. Provide a method to calculate the total price including tax
7. Make the service accessible as a utility function for use in views, models, and templates
8. Ensure the tax calculation is consistent across all parts of the application

## Constraints

1. Tax rate must be exactly 10% (0.10)
2. Input prices must be non-negative values
3. Tax calculations must handle edge cases like zero prices
4. Results must be properly formatted for currency display
5. The service should raise appropriate exceptions for invalid inputs
6. Tax calculations must be deterministic and repeatable

## References

See context.md for existing tax-related implementations and integration patterns within the Django application structure.