# Floating Point Currency Price Calculator

## Overview

This service provides precise currency calculations for e-commerce pricing operations. The system must handle monetary values with exact decimal precision to ensure accurate financial transactions and prevent rounding errors that could impact business operations or customer billing.

## Requirements

1. Create a REST endpoint that accepts a base price and calculates the final price including tax
2. Accept input parameters for base price (as decimal) and tax rate (as percentage)
3. Return the calculated total price with proper decimal precision for currency
4. Implement proper validation for input parameters to ensure they are positive values
5. Use appropriate data types that maintain precision for monetary calculations
6. Handle tax calculation by multiplying base price by (1 + tax rate)
7. Format the response to include both the original base price and calculated total
8. Ensure all monetary values are rounded to exactly 2 decimal places
9. Return appropriate HTTP status codes for successful calculations and validation errors
10. Log calculation operations for audit purposes

## Constraints

1. Base price must be greater than zero
2. Tax rate must be between 0 and 100 (inclusive)
3. All currency values must maintain exactly 2 decimal places
4. Maximum supported price value should not exceed 999,999.99
5. Input validation errors should return HTTP 400 with descriptive error messages
6. The service must handle edge cases like very small decimal values
7. Calculations must be deterministic and produce consistent results

## References

See context.md for existing currency handling patterns and decimal precision implementations used elsewhere in the codebase.