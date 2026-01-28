# Django Soft Delete Query Filtering Implementation

## Overview

This implementation provides a soft delete mechanism for Django models that allows records to be marked as deleted without physically removing them from the database. The system must automatically exclude soft-deleted records from all standard query operations while providing mechanisms to include them when explicitly requested. This pattern is commonly used in business applications where data retention is required for audit trails, compliance, or recovery purposes.

## Requirements

1. Create a custom manager that automatically excludes soft-deleted records from all default querysets
2. Implement a model mixin that adds soft delete functionality with a `deleted_at` timestamp field
3. Provide a `soft_delete()` method that marks records as deleted by setting the deletion timestamp
4. Ensure all standard query operations (filter, get, all, etc.) automatically exclude soft-deleted records
5. Provide an `include_deleted()` method on the manager to access all records including soft-deleted ones
6. Provide a `deleted_only()` method on the manager to access only soft-deleted records
7. Handle related object queries to respect soft delete status of parent objects
8. Maintain proper timezone handling for the deletion timestamp
9. Ensure the soft delete functionality works with Django's admin interface
10. Support bulk operations while respecting soft delete constraints

## Constraints

1. Soft-deleted records must remain in the database and not be physically removed
2. The `deleted_at` field must be nullable to distinguish between active and deleted records
3. Once a record is soft-deleted, it should not appear in any default queries
4. The implementation must be backward compatible with existing Django ORM patterns
5. Related object access through foreign keys must respect the soft delete status
6. The deletion timestamp must be set to the current time when soft delete is performed
7. Attempting to soft delete an already soft-deleted record should update the deletion timestamp
8. The implementation must handle timezone-aware datetime objects correctly

## References

See context.md for existing model structures and related implementations that this soft delete system should integrate with.