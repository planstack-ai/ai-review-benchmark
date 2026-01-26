# Django Performance Optimization: Eliminate Unnecessary Eager Loading

## Overview

The application needs to display a list of blog posts with their author names and comment counts. Currently, the system is experiencing performance issues due to inefficient database queries that load unnecessary related data. The goal is to optimize the query strategy to load only the required associations while maintaining the same functionality and user experience.

## Requirements

1. Display a paginated list of blog posts showing title, publication date, author name, and comment count
2. Load only the author information needed for display (name field only)
3. Retrieve comment count without loading individual comment objects
4. Ensure the solution works with Django's pagination system
5. Maintain the existing URL structure and view parameters
6. Preserve all existing template functionality and display format
7. Handle cases where posts have no comments or no author gracefully
8. Support ordering by publication date (newest first)
9. Limit database queries to avoid N+1 query problems
10. Ensure the solution is compatible with Django ORM best practices

## Constraints

1. Must not break existing template references to post.author.name
2. Must not break existing template references to comment count display
3. Cannot modify the database schema or model relationships
4. Must maintain backward compatibility with existing view logic
5. Should not load full comment objects when only count is needed
6. Must handle edge cases where related objects might be None
7. Performance optimization should not compromise data accuracy
8. Solution must work with Django's standard pagination classes

## References

See context.md for existing model definitions, view implementations, and template structure that must be preserved while optimizing the query performance.