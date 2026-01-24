# User Statistics Dashboard with Efficient Count Operations

## Overview

The application needs to display user statistics on an admin dashboard, including total counts of users, active users, and users by role. The dashboard should efficiently retrieve these statistics from the database without loading unnecessary data into memory. This feature is critical for admin users who need quick access to user metrics for reporting and monitoring purposes.

## Requirements

1. Display total count of all users in the system
2. Display count of active users (users with active status)
3. Display count of users grouped by role (admin, moderator, user)
4. All count operations must execute database COUNT queries rather than loading records into memory
5. Statistics must be retrieved in a single controller action for the dashboard
6. Count results must be displayed in a formatted statistics widget
7. The dashboard must handle cases where no users exist (zero counts)
8. All count operations must be performed efficiently without N+1 query issues

## Constraints

- Count queries must not load actual user records into application memory
- Database queries should be optimized for read performance
- The statistics must reflect real-time data from the database
- Role-based counts must handle all existing roles dynamically
- Zero counts should display as "0" rather than nil or empty values

## References

See context.md for existing User model structure and dashboard controller patterns.