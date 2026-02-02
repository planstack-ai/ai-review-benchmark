# Order-User Referential Integrity Without Foreign Keys

## Overview

The system needs to maintain data consistency between orders and users in a Rails application where foreign key constraints cannot be used at the database level. This scenario commonly occurs in legacy systems, distributed databases, or when working with external data sources that don't support referential integrity constraints. The application must ensure that orders always reference valid users and handle cases where user data becomes inconsistent.

## Requirements

1. All orders must reference a valid user through a user_id field
2. The system must prevent creation of orders with non-existent user_id values
3. The system must prevent deletion of users who have associated orders
4. When displaying orders, the system must handle cases where referenced users no longer exist
5. The system must provide a mechanism to identify and report orphaned orders (orders referencing deleted users)
6. User deletion operations must check for dependent orders before proceeding
7. Order creation must validate user existence before saving
8. The system must gracefully handle concurrent operations where a user might be deleted while an order is being created
9. All validation errors must provide clear, user-friendly messages
10. The system must maintain audit trails for user deletion attempts that fail due to existing orders

## Constraints

- Database foreign key constraints are not available and cannot be used
- User deletion should fail with a clear error message when orders exist
- Order creation should fail with validation errors for invalid user_id values
- The system must handle race conditions between user deletion and order creation
- Performance impact of validation checks should be minimized
- Orphaned order detection should not impact normal application performance
- All database operations related to referential integrity must be wrapped in appropriate transactions

## References

See context.md for existing model implementations and database schema details.