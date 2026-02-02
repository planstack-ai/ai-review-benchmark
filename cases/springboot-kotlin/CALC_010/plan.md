# Bulk Order Calculation Service

## Overview

This service implements order total calculation for an e-commerce platform that handles bulk orders. The system needs to correctly calculate totals for orders with large quantities, typically used by wholesale customers.

## Requirements

1. Create a bulk order calculation service that handles large quantity orders
2. Calculate line item totals by multiplying unit price by quantity
3. Support quantities up to 1,000,000 units per line item
4. Handle unit prices up to 10,000,000 yen
5. Ensure accurate calculations without precision loss
6. Provide clear breakdown of calculation components
7. Handle decimal precision appropriately for monetary calculations
8. Support batch processing of multiple line items

## Constraints

1. Quantities must be positive integers
2. Unit prices must be positive values
3. Calculations must handle large numbers without overflow
4. Results must maintain appropriate decimal precision
5. The service should be stateless and thread-safe
6. Maximum order total is 10 billion yen

## References

See context.md for existing order calculation patterns and service implementations in the codebase.
