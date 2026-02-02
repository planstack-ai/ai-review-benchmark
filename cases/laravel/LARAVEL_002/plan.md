# Price Attribute Formatting with Accessor and Mutator

## Overview

The system needs to handle price formatting for product display and storage. Products have a price attribute that should be stored as cents (integer) in the database but displayed as dollars (decimal) to users. The application requires both reading formatted prices for display and accepting formatted price input from users.

## Requirements

1. Store price values in the database as integers representing cents
2. Display price values to users as decimal dollars (e.g., 1299 cents displays as "12.99")
3. Accept price input from users in decimal dollar format and convert to cents for storage
4. Ensure price formatting is consistent across all product interactions
5. Handle price retrieval through model attribute access
6. Handle price assignment through model attribute assignment
7. Maintain data integrity during price conversions between cents and dollars

## Constraints

1. Price values must be non-negative integers when stored in database
2. Price display format must show exactly two decimal places
3. Price input must accept decimal values with up to two decimal places
4. Conversion between cents and dollars must be mathematically accurate
5. The price attribute must be accessible through standard Laravel model attribute syntax
6. Both getter and setter functionality must work seamlessly with Laravel's attribute system

## References

See context.md for existing codebase patterns and related implementations.