# Zero Quantity Order Validation System

## Overview

The inventory management system must prevent orders from being placed when items have zero or negative quantities available. This validation ensures that customers cannot purchase items that are out of stock, maintaining inventory accuracy and preventing overselling scenarios. The system should provide clear feedback when validation fails and maintain data integrity throughout the ordering process.

## Requirements

1. Order validation must check that all items in an order have positive quantities available in inventory
2. The system must reject orders containing any items with zero quantity
3. The system must reject orders containing any items with negative quantities
4. Validation must occur before any order processing or inventory updates
5. Clear error messages must be provided when validation fails, indicating which items are out of stock
6. The validation must handle multiple items in a single order, checking each item individually
7. Orders with valid positive quantities must be processed successfully
8. The system must maintain inventory quantity accuracy after successful order processing
9. Validation must be performed at the model or service layer, not just at the UI level
10. The system must handle edge cases such as concurrent orders that might affect inventory levels

## Constraints

- Quantity values must be treated as integers or decimals, not strings
- Zero is considered an invalid quantity for ordering purposes
- Negative quantities are invalid and should be treated as system errors
- Validation must be atomic - either all items pass validation or the entire order fails
- The system must not partially process orders that contain invalid items
- Error responses must be consistent and machine-readable for API consumers
- Inventory quantities must not be modified during validation checks

## References

See context.md for existing inventory model implementations and related order processing components.