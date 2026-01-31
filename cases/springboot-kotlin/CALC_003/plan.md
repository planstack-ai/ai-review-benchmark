# Floating Point Currency Price Calculator

## Overview

This service provides precise currency calculations for e-commerce pricing operations. The system must handle monetary values with exact decimal precision to ensure accurate financial transactions and prevent rounding errors that could lead to financial discrepancies in customer billing or merchant settlements.

## Requirements

1. Create a REST endpoint that accepts a base price and calculates the final price including tax
2. Accept input parameters for base price (as decimal) and tax rate (as percentage)
3. Return the calculated total price with proper decimal precision for currency
4. Implement proper validation for input parameters to ensure they are positive values
5. Use appropriate data types that maintain decimal precision for monetary calculations
6. Handle tax calculation by multiplying base price by (1 + tax_rate/100)
7. Return response in JSON format with clearly labeled fields
8. Implement proper HTTP status codes for successful operations and validation errors
9. Ensure all monetary values are rounded to exactly 2 decimal places in the response
10. Log calculation operations for audit purposes

## Constraints

1. Base price must be greater than zero and less than 1,000,000
2. Tax rate must be between 0 and 100 (inclusive)
3. All monetary calculations must preserve precision to avoid floating-point arithmetic errors
4. Input validation must reject null, negative, or excessively large values
5. The service must handle edge cases like very small tax rates (e.g., 0.01%)
6. Response formatting must consistently show 2 decimal places even for whole numbers

## References

See context.md for existing service patterns and architectural guidelines used in the current codebase.