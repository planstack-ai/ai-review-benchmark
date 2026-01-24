# Hide Orders for Deleted Users

## Overview

When users are deleted from the system, their associated order data should be hidden from public views and API endpoints to protect privacy and maintain data integrity. This ensures that deleted user information does not leak through order displays, while maintaining referential integrity for business records.

## Requirements

1. Orders belonging to deleted users must not appear in public order listings
2. Individual order views must return appropriate error responses when the order belongs to a deleted user
3. Order search and filtering operations must exclude orders from deleted users
4. API endpoints returning order data must filter out orders associated with deleted users
5. Admin interfaces may display orders from deleted users with appropriate indicators
6. Order statistics and reporting must account for deleted user orders appropriately
7. Related order data (items, payments, shipments) must be handled consistently with the parent order visibility rules

## Constraints

1. Soft-deleted users (marked as deleted but not physically removed) must be treated as deleted users
2. Orders must maintain referential integrity even when users are deleted
3. Historical business data requirements may necessitate preserving order records internally
4. Performance impact of filtering operations must be minimized through appropriate indexing
5. Cascade deletion rules must be clearly defined for related entities

## References

See context.md for existing user deletion patterns, order model relationships, and current authorization implementations.