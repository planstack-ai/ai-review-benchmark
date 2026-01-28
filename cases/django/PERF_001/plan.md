# Order Management System with Efficient Product Loading

## Overview

The system manages customer orders containing multiple order items, where each order item references a specific product. The business requires displaying order summaries that include product details (name, price, description) alongside order item quantities and subtotals. This functionality is critical for order confirmation pages, administrative dashboards, and customer order history views where performance is essential.

## Requirements

1. Create an Order model that stores customer information and order metadata
2. Create an OrderItem model that links orders to products with quantity information
3. Create a Product model that stores product details including name, price, and description
4. Implement a view function that retrieves all orders with their associated order items and product information
5. Ensure the view loads all necessary data in a single database query operation to avoid multiple round trips
6. The view must return order data that includes product names, prices, and calculated subtotals for each order item
7. Implement proper foreign key relationships between Order, OrderItem, and Product models
8. The system must handle orders with multiple items efficiently regardless of the number of items per order
9. Product information must be immediately accessible from order item objects without triggering additional database queries

## Constraints

1. Orders must have at least one order item to be considered valid
2. Order items must reference existing products
3. Quantities in order items must be positive integers
4. Product prices must be positive decimal values
5. The solution must work efficiently with orders containing 1 to 100+ items
6. Database queries must be optimized to prevent N+1 query problems

## References

See context.md for existing model definitions and database schema requirements.