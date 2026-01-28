# User Profile Management with Optimized Related Data Loading

## Overview

A user profile management system that displays user information along with their associated posts and comments. The system needs to efficiently load and display user profiles with their related content to provide a comprehensive view for administrators and users themselves. The application must handle scenarios where users have varying amounts of associated content while maintaining optimal database performance.

## Requirements

1. Create a User model with basic profile information including username, email, first_name, and last_name fields
2. Create a Post model that belongs to a User with title, content, and creation timestamp fields
3. Create a Comment model that belongs to both a User and a Post with content and creation timestamp fields
4. Implement a view that displays a list of users with their post count and latest comment
5. Use Django ORM methods to preload related data in a single database query to prevent N+1 query problems
6. Display user information including username, email, total number of posts, and their most recent comment content
7. Handle cases where users may have no posts or comments gracefully
8. Ensure the view loads all necessary data efficiently regardless of the number of users in the system
9. Implement proper model relationships using Django's foreign key fields
10. Structure the code to be maintainable and follow Django best practices for query optimization

## Constraints

1. The solution must use Django ORM's select_related() or prefetch_related() methods appropriately
2. All related data must be loaded in the initial query, not through subsequent database calls
3. The view must handle users with zero posts or comments without causing errors
4. Database queries should be minimized regardless of the number of users being displayed
5. Model relationships must be properly defined with appropriate on_delete behaviors

## References

See context.md for existing model structures and query patterns used in similar implementations.