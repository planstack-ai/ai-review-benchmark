# Zero Quantity Order Validation

## Overview

The inventory management system must prevent orders from being processed when items have zero or negative quantities. This validation ensures data integrity and prevents invalid business transactions that could lead to overselling or negative inventory states.

## Requirements

1. The system must validate that item quantities are greater than zero before processing any order
2. When an item quantity is zero, the system must reject the order with an appropriate error message
3. When an item quantity is negative, the system must reject the order with an appropriate error message
4. The validation must occur before any inventory updates are committed to the database
5. Error messages must clearly indicate which item(s) have invalid quantities
6. The system must handle validation for single-item orders
7. The system must handle validation for multi-item orders, checking each item individually
8. Valid orders with positive quantities must be processed successfully without interference from the validation

## Constraints

- Quantity validation must be performed on integer values only
- Zero is considered an invalid quantity for ordering purposes
- Fractional quantities are not supported in this system
- The validation must not modify the original order data during the check process
- Database transactions must be rolled back if validation fails after starting

## References

See context.md for existing inventory management patterns and validation implementations used throughout the codebase.