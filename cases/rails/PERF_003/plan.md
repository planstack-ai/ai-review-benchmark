# User Activity Dashboard with Optimized Association Loading

## Overview

The system needs to display a user activity dashboard that shows user information along with their recent posts and comments. The dashboard should efficiently load only the data that will actually be displayed to users, avoiding unnecessary database queries and memory usage. The feature serves as a performance-critical component that may handle high traffic volumes.

## Requirements

1. Display a list of users with their basic information (name, email, created_at)
2. Show the count of posts for each user without loading the actual post records
3. Show the count of comments for each user without loading the actual comment records
4. Display the user's most recent post title only (if any exists)
5. Display the user's most recent comment content only (if any exists)
6. Implement pagination to handle large datasets efficiently
7. Ensure the solution minimizes database queries through appropriate association loading
8. Load only the specific data fields that will be displayed in the view
9. Avoid loading full associated records when only aggregate data or single records are needed

## Constraints

1. The dashboard must handle users who have no posts or comments gracefully
2. Database queries should be optimized to prevent N+1 query problems
3. Memory usage should be minimized by not loading unnecessary association data
4. The solution must work with standard Rails association methods
5. Performance should remain consistent regardless of the number of associations per user

## References

See context.md for existing User, Post, and Comment model implementations and their associations.