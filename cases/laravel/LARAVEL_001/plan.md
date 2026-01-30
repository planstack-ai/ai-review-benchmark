# Product Catalog Active Filter Implementation

## Overview

The product catalog system needs to display only active products to customers browsing the website. This feature ensures that discontinued, out-of-stock, or temporarily disabled products are automatically filtered out from all customer-facing product listings without requiring manual intervention from developers.

## Requirements

1. Create a database-level filter that excludes inactive products from query results
2. Implement the filter as a reusable component that can be applied to product queries
3. Apply the active product filter to the main product catalog listing page
4. Ensure the filter works with pagination and maintains performance
5. The filter should be based on a boolean status field in the products table
6. Only products with active status should appear in customer-facing catalog views
7. The filtering mechanism should be automatically applied without requiring additional query modifications
8. Maintain compatibility with existing product search and sorting functionality

## Constraints

1. The filter must not affect administrative views where inactive products need to be visible
2. Database queries should remain efficient and not cause N+1 query problems
3. The implementation should follow Laravel best practices for query scoping
4. The filter should be easily testable and maintainable
5. Must preserve existing URL parameters and query string functionality

## References

See context.md for existing product model structure and current catalog implementation patterns.