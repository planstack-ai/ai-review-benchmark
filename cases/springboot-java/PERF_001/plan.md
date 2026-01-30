# Order Items with Products Eager Loading

## Overview

The system needs to display order details including associated product information. When retrieving orders, the application must efficiently load both order items and their corresponding product data to avoid performance issues when rendering order summaries or detailed views.

## Requirements

1. The system must retrieve orders with their associated order items efficiently
2. Product information for each order item must be loaded alongside the order items
3. The implementation must prevent multiple database queries when accessing product details for order items
4. Order retrieval should use JPA best practices for eager loading nested associations
5. The solution must work for both single order retrieval and multiple order collections
6. Product attributes (name, price, description) must be accessible without triggering additional queries
7. The implementation must maintain referential integrity between orders, order_items, and products

## Constraints

1. Orders without order items should still be retrievable
2. Order items without associated products should be handled gracefully
3. The solution must not break existing order retrieval functionality
4. Database query count must remain constant regardless of the number of order items per order
5. Memory usage should be reasonable for large order collections

## References

See context.md for existing entity associations and database schema details.
