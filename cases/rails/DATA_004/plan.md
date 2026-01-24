# Soft Delete Query Filtering Implementation

## Overview

The application needs to implement soft delete functionality where records are marked as deleted rather than physically removed from the database. All standard queries must automatically exclude soft-deleted records to maintain data integrity and prevent deleted content from appearing in the application. This ensures that deleted records remain in the database for audit purposes while being invisible to normal application operations.

## Requirements

1. All model queries must automatically exclude records where the `deleted_at` field is not null
2. The soft delete filtering must be applied to all standard ActiveRecord query methods (find, where, all, etc.)
3. Soft-deleted records must be excluded from associations and related queries
4. The system must provide a way to explicitly include soft-deleted records when needed for administrative purposes
5. Soft delete filtering must work consistently across all models that implement soft delete functionality
6. The filtering mechanism must not interfere with record creation, updates, or explicit deletion operations
7. Queries that explicitly search for soft-deleted records (where deleted_at is not null) must work correctly
8. The implementation must handle edge cases where deleted_at field might have various timestamp values

## Constraints

1. The deleted_at field must be a datetime/timestamp column that is null for active records
2. Soft delete filtering must not apply when explicitly querying for deleted records
3. The implementation must not break existing query chains or scopes
4. Performance impact on queries must be minimal
5. The filtering must work with both simple queries and complex joins
6. Administrative interfaces may need to bypass soft delete filtering with explicit parameters

## References

See context.md for existing model implementations and database schema details.