# Master Data History for Order Items

## Overview

When customers place orders, the system must preserve the exact product information as it existed at the time of purchase. This ensures that historical order data remains accurate even when product details (name, price, description, etc.) are updated in the master product catalog. This feature is critical for maintaining order integrity, supporting customer service inquiries, and ensuring accurate financial reporting over time.

## Requirements

1. Order items must capture and store product name at the time of order creation
2. Order items must capture and store product price at the time of order creation
3. Order items must capture and store product description at the time of order creation
4. Order items must capture and store product SKU at the time of order creation
5. Order items must maintain a reference to the original product record for future lookups
6. Historical product data in order items must remain unchanged when the master product record is updated
7. Order items must calculate and store the total line amount based on quantity and captured price
8. The system must support querying order items independently of current product state
9. Order creation must fail if required product information cannot be captured
10. All captured product data must be stored in the order items table, not referenced from the products table

## Constraints

1. Product price must be greater than zero when captured
2. Product SKU must be unique and non-empty when captured
3. Product name and description cannot be null or empty when captured
4. Order items cannot be created without a valid product reference
5. Captured product data cannot be modified after order item creation
6. The original product ID reference must remain valid even if the product is soft-deleted

## References

See context.md for existing Product and Order model implementations and database schema details.