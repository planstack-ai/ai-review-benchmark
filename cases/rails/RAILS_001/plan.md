# Active User Management System

## Overview

The system needs to manage user accounts with different status levels. Users can be active, inactive, or suspended. The application requires functionality to retrieve and display only active users for various business operations, such as user listings, notifications, and administrative reports. This ensures that inactive or suspended users are excluded from normal business workflows while maintaining data integrity.

## Requirements

1. The system must provide a way to filter users based on their active status
2. User listings must display only users with active status
3. The filtering mechanism must be reusable across different parts of the application
4. The system must handle cases where no active users exist
5. The active user filtering must be efficient and not perform unnecessary database queries
6. The implementation must leverage existing database-level filtering capabilities
7. The user status determination must be consistent throughout the application

## Constraints

- Users have a status field that determines their active state
- Only users with 'active' status should be considered active
- The system must not modify user status when retrieving active users
- Database queries should be optimized to filter at the database level rather than in application memory
- The solution must be maintainable and follow Rails conventions

## References

See context.md for existing User model implementation and available scope definitions.