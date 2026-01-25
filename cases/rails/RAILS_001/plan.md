# Product Analytics Service

## Overview

The system needs to provide analytics and reporting functionality for products. This includes generating reports on active products, calculating revenue metrics, tracking top performers, monitoring inventory levels, and exporting product data. The service should leverage existing model scopes and follow Rails conventions for maintainability.

## Requirements

1. Generate comprehensive product reports including active product counts, revenue by category, and top performers
2. Export active products to CSV format with relevant details (name, category, price, stock, rating)
3. Provide bulk pricing update functionality for active products
4. Calculate conversion rates based on product views and purchases
5. Monitor inventory levels to identify low stock and out of stock items
6. All queries for active products must use the existing `Product.active` scope for consistency

## Constraints

- Products have a status field with values: 'active', 'inactive', 'discontinued'
- Only products with 'active' status should be included in analytics
- The implementation must use existing model scopes rather than inline query conditions
- Database queries should be optimized and follow Rails conventions
- The solution must be DRY - avoid repeating query logic across methods

## References

See context.md for existing Product model implementation and the `Product.active` scope definition.
