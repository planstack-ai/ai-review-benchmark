# Bulk User Status Update System

## Overview

The system needs to support bulk status updates for user accounts during administrative operations. This feature is specifically designed for scenarios where administrators need to update multiple user records simultaneously without triggering individual user callbacks that would normally send notifications, update timestamps, or perform other side effects that are unnecessary during bulk operations.

## Requirements

1. Implement a method that can update the status field for multiple users in a single database operation
2. The bulk update operation must bypass ActiveRecord callbacks to avoid performance overhead
3. Support updating users based on a collection of user IDs
4. Allow specifying the target status value for the bulk update
5. Return the number of affected records after the operation completes
6. Ensure the operation is atomic - either all specified records are updated or none are updated
7. Validate that the provided status value is within the allowed status enumeration values
8. Handle cases where some of the provided user IDs may not exist in the database
9. Log the bulk update operation for audit purposes including the number of records affected

## Constraints

1. The bulk update must not trigger any ActiveRecord callbacks (before_update, after_update, etc.)
2. Only users with existing records in the database should be considered for updates
3. The status field must be validated against the User model's status enum values
4. The operation should be performed as a single SQL UPDATE statement for performance
5. Invalid user IDs should be silently ignored rather than causing the entire operation to fail
6. The method should handle empty input arrays gracefully without performing unnecessary database queries

## References

See context.md for existing User model implementation and status enumeration definitions.