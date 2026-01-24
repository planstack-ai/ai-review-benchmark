# User Activity Dashboard with Optimized Data Loading

## Overview

The system needs to display a user activity dashboard that shows users along with their recent posts and associated comments. The dashboard must efficiently load and display this hierarchical data while maintaining good performance characteristics. Users should be able to view a paginated list of users with their activity metrics and recent content.

## Requirements

1. Display a paginated list of users (25 users per page)
2. For each user, show their total post count
3. For each user, display their 3 most recent posts
4. For each displayed post, show the comment count
5. For each displayed post, show the first 2 comments with author names
6. Implement efficient database querying to minimize N+1 query problems
7. Load all necessary data in a single database round-trip where possible
8. Ensure the solution scales well with increasing numbers of users, posts, and comments
9. Display users ordered by their registration date (newest first)
10. Handle cases where users have no posts or posts have no comments gracefully

## Constraints

1. The page must load within acceptable performance limits (< 500ms database query time)
2. Database queries should be optimized to avoid loading unnecessary data
3. The solution must work with standard Rails associations (User has_many Posts, Post has_many Comments, Comment belongs_to User)
4. Memory usage should be reasonable even with large datasets
5. The implementation should follow Rails best practices for data loading
6. Must handle edge cases where associations return empty collections

## References

See context.md for existing model definitions, associations, and controller structure that should be leveraged in the implementation.