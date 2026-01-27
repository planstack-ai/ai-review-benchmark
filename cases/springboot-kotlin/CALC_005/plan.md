# Tax Calculation Service with Fixed Rate

## Overview

This service provides tax calculation functionality for an e-commerce platform. The system must apply a standardized tax rate to product prices to determine the total amount customers need to pay. The tax calculation is a critical component that affects order processing, pricing display, and financial reporting.

## Requirements

1. Create a REST endpoint that accepts a product price and returns the total amount including tax
2. Apply a fixed tax rate of 10% to all calculations
3. Accept price input as a decimal number with up to 2 decimal places
4. Return the calculated total amount rounded to 2 decimal places
5. Handle price inputs greater than zero
6. Provide appropriate HTTP status codes for successful and error responses
7. Include proper request and response data validation
8. Return results in JSON format with clear field names

## Constraints

1. Price input must be a positive number greater than zero
2. Price input cannot exceed 999999.99 (maximum supported amount)
3. Tax rate must remain constant at 10% and not be configurable
4. All monetary calculations must maintain precision to avoid rounding errors
5. Invalid input should return appropriate error messages
6. Null or empty price values should be rejected

## References

See context.md for existing service patterns and architectural guidelines used in the codebase.