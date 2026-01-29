# Order Items Entity Mapping

## Overview

Define the relationship between orders and order items. When an order is deleted, associated order items should be properly handled to maintain database integrity.

## Requirements

1. Order items must be associated with an order
2. Deleting an order should handle associated order items
3. No orphan order_item records should exist without a parent order
4. Support cascading operations where appropriate
5. Maintain referential integrity at database level

## Constraints

1. Database must enforce foreign key relationships
2. Deletion of parent should not leave orphan children
3. Must work with existing schema
4. Performance should not be significantly impacted

## References

See context.md for existing schema definitions.
