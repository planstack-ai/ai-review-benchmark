# Laravel Observer for Order-Inventory Transaction Management

## Overview

This system implements an automated inventory management solution that responds to order creation events. When a new order is placed in the e-commerce system, the inventory levels for the ordered products must be automatically decremented to maintain accurate stock counts. This functionality is critical for preventing overselling and maintaining data consistency between the order and inventory systems.

## Requirements

1. Create an Observer class that listens to Order model events
2. Implement automatic inventory reduction when an order is successfully created
3. Decrease inventory quantity by the ordered amount for each product in the order
4. Ensure inventory updates occur within the same database transaction as order creation
5. Handle orders containing multiple products with different quantities
6. Prevent inventory from going below zero during the update process
7. Log inventory changes for audit trail purposes
8. Maintain referential integrity between orders and inventory records
9. Register the Observer with the Order model through the appropriate service provider
10. Ensure the inventory update process is atomic and rollback-safe

## Constraints

1. Inventory quantity cannot be reduced below zero
2. All inventory updates must complete successfully or the entire order creation must fail
3. The system must handle concurrent order processing without race conditions
4. Only process inventory updates for orders with 'confirmed' or 'paid' status
5. Skip inventory updates for orders marked as 'draft' or 'cancelled'
6. Validate that all products in the order exist in the inventory table before processing
7. Ensure sufficient stock is available before allowing the order to be created
8. Handle cases where products may be discontinued or temporarily unavailable

## References

See context.md for existing Order model structure, Inventory model relationships, and current database schema implementation.