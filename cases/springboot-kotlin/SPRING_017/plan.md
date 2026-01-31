# SPRING_017: Load orders with items and products

## Overview

Implement order detail view that loads order with all related data: order items, product details, and payment records.

## Requirements

1. Load order by ID with all related data:
   - Order items (collection)
   - Product details for each item
   - Payment records (collection)
2. Avoid N+1 query problem
3. Single database query preferred for performance
4. All data needed for order detail page

## Constraints

- Must fetch all related entities in single query
- Cannot use lazy loading (may cause N+1 queries)
- Response time should be fast
- Order detail page needs all related data

## References

- JPA @EntityGraph
- Fetch strategies (LAZY vs EAGER)
- N+1 query problem
- JPA fetch joins
