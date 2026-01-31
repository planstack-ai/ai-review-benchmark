# Tax Calculation Service with Fixed Rate

## Overview

The system requires a tax calculation service that applies a standardized tax rate to monetary amounts. This service will be used across the application to ensure consistent tax calculations for financial transactions, product pricing, and billing operations. The tax rate is currently set at 10% and should be applied uniformly to all taxable amounts.

## Requirements

1. Create a service class that calculates tax amounts for given monetary values
2. Apply a fixed tax rate of 10% to all calculations
3. Accept decimal input values representing monetary amounts
4. Return the calculated tax amount as a decimal value
5. Expose the tax calculation functionality through a REST API endpoint
6. The endpoint should accept a monetary amount as input parameter
7. The endpoint should return the calculated tax amount in the response
8. Handle standard HTTP methods appropriately for the calculation operation
9. Ensure the service can be injected and used by other components
10. Maintain precision appropriate for financial calculations

## Constraints

1. Input amounts must be non-negative values
2. The tax rate must remain constant at 10% throughout the application
3. Calculations should handle decimal precision without rounding errors
4. Invalid input should result in appropriate error responses
5. The service should not accept null or negative monetary amounts
6. API responses should follow standard JSON format
7. The tax rate should not be configurable or modifiable at runtime

## References

See context.md for examples of existing service implementations and API patterns used in the codebase.