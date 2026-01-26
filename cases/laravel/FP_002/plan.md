# Order Processing Service

## Overview

Service to process customer orders with transactional inventory management.

## Requirements

1. Validate order items exist and are available before processing
2. Calculate order totals correctly (subtotal + 10% tax)
3. Create order and order items atomically
4. Update inventory (decrement stock) after order creation

## Constraints

1. All database operations must be wrapped in a transaction
2. Inventory must be validated before order creation
3. Stock check during decrement prevents negative inventory

## Notes

- The service uses Laravel's DB transaction support
- Stock decrement includes a where clause to prevent overselling
