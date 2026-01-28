# E-commerce Product Catalog with Optimized Denormalization

## Overview

An e-commerce platform needs to display product listings with category information, ratings, and inventory status. The system must handle high read traffic for product browsing while maintaining data consistency. Products belong to categories, have multiple reviews that contribute to average ratings, and have inventory tracking across multiple warehouses.

## Requirements

1. Product model must store denormalized category name alongside category foreign key for faster queries
2. Product model must maintain a denormalized average rating field that updates when reviews are added or modified
3. Product model must include a denormalized total review count field
4. Product model must have a denormalized in-stock boolean field based on inventory levels across warehouses
5. Category name denormalization must update automatically when category names change
6. Rating denormalization must recalculate when reviews are created, updated, or deleted
7. Stock status denormalization must update when inventory levels change in any warehouse
8. All denormalized fields must be kept in sync using Django signals or model methods
9. Product listing views must use denormalized fields to avoid JOIN operations
10. System must provide management commands to rebuild denormalized data for data integrity maintenance

## Constraints

1. Denormalized fields must never become permanently inconsistent with source data
2. Rating calculations must handle division by zero when no reviews exist
3. Stock status must be false if total inventory across all warehouses is zero or negative
4. Category name updates must propagate to all associated products atomically
5. Signal handlers must be efficient and avoid N+1 query problems during bulk operations

## References

See context.md for existing model relationships and database schema patterns used in the codebase.