# User Activity Tracking with Standard Scopes

## Overview

The application needs to track user activity and provide filtering capabilities for administrative purposes. Users have different activity states, and administrators need to query users based on their activity status using standard Rails scope patterns. This feature supports user management workflows where filtering by activity level is essential for monitoring and maintenance tasks.

## Requirements

1. Implement a User model with activity tracking capabilities
2. Create standard Rails scopes for filtering users by activity status
3. Provide scope for active users who have logged in recently
4. Provide scope for inactive users who haven't logged in for an extended period
5. Include a scope for users who have never logged in
6. Ensure scopes follow Rails naming conventions and return ActiveRecord::Relation objects
7. Support method chaining with other scopes and query methods
8. Include appropriate database fields to support activity tracking functionality

## Constraints

- Scopes must be defined using the standard Rails `scope` method
- Activity determination should be based on login timestamps
- Inactive period threshold should be configurable through application settings
- All scopes must handle nil values gracefully
- Scopes should be efficient and avoid N+1 query problems

## References

See context.md for existing user management patterns and database schema considerations.