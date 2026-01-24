# Tax Calculation Service Implementation

## Overview

The system requires a tax calculation service that applies the current standard tax rate to monetary amounts. This service will be used across the application to ensure consistent tax calculations for financial transactions, product pricing, and invoice generation.

## Requirements

1. Create a tax calculation service that accepts a base amount as input
2. Apply a tax rate of 10% to the provided base amount
3. Return the calculated tax amount as a separate value
4. Return the total amount (base amount plus tax) as a separate value
5. Handle decimal precision appropriately for monetary calculations
6. Accept numeric input types (integers, floats, decimals)
7. Provide a clear and intuitive interface for tax calculations

## Constraints

1. Tax rate must be exactly 10% (0.10)
2. Input amounts must be non-negative values
3. Calculated values should maintain appropriate decimal precision for currency
4. Service must handle zero amounts correctly
5. Invalid input types should be handled gracefully
6. Negative amounts should be rejected or handled according to business rules

## References

See context.md for existing tax calculation patterns and integration points within the current codebase.