# Bulk Product Price Update System

## Overview

The system needs to efficiently update prices for large numbers of products in an e-commerce platform. When processing bulk price updates from suppliers or during promotional campaigns, the system must prioritize performance over individual record tracking. This operation is intentionally designed to bypass Django's model signals to avoid the overhead of triggering post-save operations for thousands of records simultaneously.

## Requirements

1. The system must provide a method to update product prices in bulk using Django's bulk_update functionality
2. The bulk update operation must intentionally skip Django model signals (pre_save, post_save, etc.) for performance optimization
3. The system must accept a list of product objects with updated price fields
4. The bulk update must target only the price-related fields (price, sale_price, cost) to minimize database operations
5. The operation must be performed within a single database transaction for data consistency
6. The system must handle empty product lists gracefully without raising exceptions
7. The method must return the number of records successfully updated
8. The implementation must use Django's QuerySet.bulk_update() method with explicit field specification
9. The system must validate that all provided products have valid price values before performing the update
10. The bulk update operation must be atomic - either all records update successfully or none do

## Constraints

1. Price values must be non-negative decimal numbers
2. The bulk update should not exceed 1000 records per batch to avoid database timeout issues
3. Products must exist in the database before attempting to update their prices
4. The operation must not trigger any model validation beyond basic field type checking
5. Concurrent bulk updates on the same products should be handled through database-level locking

## References

See context.md for existing Product model structure and related bulk operation patterns used elsewhere in the codebase.