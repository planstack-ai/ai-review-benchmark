# Order Status Management System

## Overview

The system needs to manage order statuses in an e-commerce application. Orders progress through various states from creation to completion, and the system must track these status changes efficiently. The status field should provide type safety, database-level constraints, and convenient query methods to ensure data integrity and improve developer experience.

## Requirements

1. The Order model must have a status field that tracks the current state of an order
2. The status field must use Rails enum functionality to define allowed status values
3. The enum must include the following status values: pending, processing, shipped, delivered, cancelled
4. The status field must have a default value of "pending" for new orders
5. The enum must provide automatic scope methods for querying orders by status
6. The enum must provide automatic predicate methods for checking order status
7. The status field must be properly indexed in the database for query performance
8. The enum must prevent invalid status values from being assigned
9. Status transitions must be trackable and the current status must always be accessible
10. The implementation must follow Rails conventions for enum naming and structure

## Constraints

1. Status values must be stored as integers in the database for performance
2. The enum must not allow nil values for the status field
3. Status changes must not break existing functionality or queries
4. The implementation must be compatible with Rails 6+ enum features
5. Database migration must handle existing data appropriately if any exists

## References

See context.md for existing Order model implementation and related database schema.