# User Profile Management with Cascade Delete

## Overview

The system manages user profiles and their associated data including posts, comments, and profile settings. When a user account is deleted, all related data must be automatically removed to maintain data integrity and comply with data retention policies. This ensures no orphaned records remain in the database after user deletion.

## Requirements

1. User model must automatically delete all associated posts when a user is deleted
2. User model must automatically delete all associated comments when a user is deleted
3. User model must automatically delete the associated profile when a user is deleted
4. Post model must automatically delete all associated comments when a post is deleted
5. All cascade deletions must occur within the same database transaction
6. The system must handle deletion of users with large numbers of associated records efficiently
7. Deletion operations must maintain referential integrity across all related tables
8. The cascade delete behavior must be implemented at the ActiveRecord model level

## Constraints

1. Users cannot be deleted if they have pending administrative actions
2. System must log all cascade deletion operations for audit purposes
3. Deletion operations must complete within 30 seconds for users with up to 10,000 associated records
4. Foreign key constraints must be properly maintained during cascade operations
5. The system must handle concurrent deletion attempts gracefully

## References

See context.md for existing model relationships and database schema details.