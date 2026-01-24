# User Activity Dashboard with Optimized Data Loading

## Overview

The system needs to display a user activity dashboard that shows users along with their recent posts and associated comments. This is a common scenario where multiple related records need to be displayed together, requiring careful attention to database query optimization to prevent N+1 query problems that could severely impact performance as the dataset grows.

## Requirements

1. Display a list of users with their basic information (name, email)
2. For each user, show their 3 most recent posts with post titles and creation dates
3. For each post, display the total count of associated comments
4. Load all necessary data efficiently to avoid multiple database queries per user or post
5. Implement proper eager loading to fetch users, posts, and comment counts in minimal database queries
6. Ensure the solution scales well with increasing numbers of users and posts
7. Display the data in a clean, organized format showing the hierarchical relationship between users, posts, and comment counts

## Constraints

1. Only show the 3 most recent posts per user, ordered by creation date descending
2. Comment counts should be accurate and reflect the current state of the database
3. Handle users with no posts gracefully (still display the user information)
4. Handle posts with no comments gracefully (display count as 0)
5. The solution must work with standard Rails associations and ActiveRecord methods

## References

See context.md for existing User, Post, and Comment model implementations and their associations.