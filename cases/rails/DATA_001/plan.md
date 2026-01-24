# User Profile Management Without Foreign Key Constraints

## Overview

The system needs to manage user profiles and their associated posts in a blogging platform. Due to legacy database constraints, foreign key relationships cannot be enforced at the database level. The application must maintain referential integrity through application-level logic to ensure data consistency when users are deleted or posts are orphaned.

## Requirements

1. Create a User model with basic profile information (name, email, created_at, updated_at)
2. Create a Post model with content fields (title, body, user_id, created_at, updated_at)
3. Establish a one-to-many relationship between users and posts without database foreign key constraints
4. Implement application-level referential integrity when deleting users
5. Handle orphaned posts appropriately when their associated user no longer exists
6. Provide methods to safely query posts with valid user associations
7. Ensure user deletion operations maintain data consistency
8. Implement validation to prevent creation of posts with invalid user references
9. Add appropriate model associations and helper methods for accessing related data
10. Handle edge cases where user_id references may become invalid

## Constraints

- Database foreign key constraints are not available and cannot be used
- User deletion must not leave orphaned posts with invalid user_id references
- Posts must always reference valid, existing users
- System must gracefully handle queries for posts whose users have been deleted
- Data integrity must be maintained entirely through application logic
- Performance should be considered when implementing referential integrity checks

## References

See context.md for existing database schema and model structure examples.