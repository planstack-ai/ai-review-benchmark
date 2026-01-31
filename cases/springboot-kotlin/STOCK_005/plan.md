# Order Item Quantity Validation

## Overview

This system processes orders for an e-commerce platform. Each order contains one or more order items, with each item specifying a product and the quantity to be purchased. The system must validate that all order items have valid, positive quantities before processing the order. Zero or negative quantities should not be allowed as they represent invalid order requests.

## Requirements

1. The system shall provide an endpoint to create orders with multiple items
2. Each order item must specify a valid product ID and quantity
3. Item quantities must be positive integers (greater than zero)
4. The system shall reject orders containing items with zero quantity
5. The system shall reject orders containing items with negative quantity
6. Validation must occur before any stock allocation or payment processing
7. Clear error messages must be provided when invalid quantities are detected
8. The system shall validate all items in an order, not just the first invalid one
9. Valid orders with positive quantities should be processed successfully
10. The validation rules must be enforced at the entity level and service level

## Constraints

1. Order items must reference valid product IDs
2. Quantities must be represented as integers
3. The minimum valid quantity is 1
4. There is no explicit maximum quantity constraint in this validation
5. Empty orders (no items) should also be rejected
6. The system must prevent database insertion of invalid quantity values
7. Validation errors should be returned before any side effects occur

## References

See context.md for existing order processing implementations, validation patterns, and database schema details.
