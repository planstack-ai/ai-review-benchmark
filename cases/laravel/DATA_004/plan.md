# Soft Delete Query Implementation for Product Catalog

## Overview

The product catalog system needs to properly handle soft-deleted products by excluding them from all customer-facing queries. Products should be marked as deleted using a timestamp field rather than being physically removed from the database, allowing for data recovery and audit trails while maintaining a clean customer experience.

## Requirements

1. All product listing queries must exclude soft-deleted products by default
2. Soft-deleted products must be identified by a non-null `deleted_at` timestamp field
3. Product search functionality must not return soft-deleted products
4. Category-based product filtering must exclude soft-deleted products
5. Featured product selections must exclude soft-deleted products
6. Product recommendation algorithms must not include soft-deleted products
7. Inventory counts and statistics must exclude soft-deleted products
8. Public API endpoints returning product data must exclude soft-deleted products

## Constraints

1. Admin interfaces may need to access soft-deleted products for recovery purposes
2. Soft-deleted products must remain accessible through direct database queries for reporting
3. Related product associations (reviews, orders) must remain intact when products are soft-deleted
4. The `deleted_at` field must use the application's configured timezone
5. Bulk operations on products must respect soft-delete status
6. Product URLs for soft-deleted items should return appropriate HTTP status codes

## References

See context.md for existing model definitions and database schema information.