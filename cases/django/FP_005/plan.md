# Bulk Product Price Update System

## Overview

The system needs to efficiently update prices for multiple products simultaneously without triggering individual model signals or post-save hooks. This is designed for administrative bulk operations where performance is critical and individual product change notifications are not required.

## Requirements

1. Implement a bulk update mechanism that can modify multiple product prices in a single database operation
2. The bulk update must bypass Django's standard model signals (pre_save, post_save, etc.)
3. Support updating prices for products identified by a list of product IDs
4. Accept a uniform price value to apply to all specified products
5. Return the count of successfully updated products
6. Handle the case where some specified product IDs may not exist in the database
7. Ensure the operation is atomic - either all valid updates succeed or none do
8. Maintain data integrity by validating that price values are positive numbers
9. Log the bulk update operation for audit purposes
10. Provide appropriate error handling for database connection issues

## Constraints

1. Price values must be greater than zero
2. Product IDs must be valid integers
3. The bulk update should not trigger any model-level validation that would normally occur during individual saves
4. Maximum batch size should be configurable to prevent memory issues with very large datasets
5. The operation should complete within reasonable time limits for typical batch sizes (up to 1000 products)

## References

See context.md for existing product model structure and related bulk operation patterns used elsewhere in the codebase.