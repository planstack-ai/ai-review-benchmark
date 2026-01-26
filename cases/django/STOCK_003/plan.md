# Cart Stock Divergence Validation System

## Overview

An e-commerce inventory management system requires robust stock validation during the checkout process to prevent overselling. The system must handle scenarios where product stock levels change between the time items are added to a cart and when the customer attempts to complete their purchase. This feature ensures data integrity and provides clear feedback to customers when stock availability changes.

## Requirements

1. Implement a stock validation mechanism that checks current inventory levels against cart quantities during checkout initiation
2. Compare cart item quantities with real-time stock availability from the inventory system
3. Generate detailed validation reports identifying which items have insufficient stock
4. Provide specific quantity information showing requested amounts versus available stock for each problematic item
5. Block checkout completion when any cart item exceeds available inventory
6. Return structured error responses containing item identifiers, requested quantities, and available quantities
7. Handle cases where products become completely out of stock after being added to cart
8. Process validation for multiple items in a single cart transaction
9. Maintain cart state while preventing purchase of unavailable quantities
10. Log stock validation attempts and results for audit purposes

## Constraints

1. Stock validation must occur immediately before payment processing begins
2. Validation must use current database values, not cached inventory data
3. All cart items must pass stock validation for checkout to proceed
4. Error messages must clearly identify which specific items and quantities are problematic
5. The system must handle concurrent access scenarios where stock levels change during validation
6. Validation results must include both human-readable messages and structured data for API consumers
7. Out-of-stock items must be clearly distinguished from items with insufficient (but non-zero) quantities

## References

See context.md for existing Cart, Product, and inventory management model implementations.