# Member Discount Rate Calculation Service

## Overview

This service implements a discount calculation system for an e-commerce platform that provides preferential pricing to registered members. The system needs to differentiate between regular customers and members, applying appropriate discount rates to calculate final pricing for orders.

## Requirements

1. Create a discount calculation service that accepts customer type and order amount as inputs
2. Apply a 10% discount rate for customers identified as members
3. Apply no discount (0%) for non-member customers
4. Return the discounted amount as the final calculation result
5. Handle decimal precision appropriately for monetary calculations
6. Implement proper input validation for order amounts
7. Use appropriate data types for financial calculations
8. Provide clear method signatures that indicate the discount calculation purpose

## Constraints

1. Order amounts must be positive values greater than zero
2. Discount rates must be expressed as percentages (0-100 range)
3. Member status must be clearly identifiable through input parameters
4. Calculated discount amounts should maintain appropriate decimal precision
5. Invalid inputs should be handled gracefully with appropriate error responses
6. The service should be stateless and thread-safe

## References

See context.md for existing discount calculation patterns and service implementations in the codebase.