# User Profile Dashboard with Optimized Data Loading

## Overview

A user profile dashboard system that displays comprehensive user information including their posts, comments, and associated metadata. The system is designed to handle high-traffic scenarios where multiple related data entities need to be efficiently loaded to prevent database performance issues. The dashboard serves as a central hub for users to view their activity and engagement metrics across the platform.

## Requirements

1. Display user profile information including basic details, statistics, and activity summary
2. Show a list of the user's recent posts with their associated categories and tags
3. Display recent comments made by the user along with the posts they commented on
4. Include engagement metrics such as like counts, comment counts, and view statistics
5. Load all necessary related data in a single database query operation to avoid multiple round trips
6. Ensure the page loads efficiently even when users have large amounts of associated content
7. Present the information in a structured format that allows users to quickly navigate their content
8. Handle cases where users may have no posts or comments gracefully
9. Display timestamps for all user activities in a user-friendly format
10. Provide accurate counts and statistics without requiring additional database queries

## Constraints

1. The dashboard must load within acceptable performance thresholds regardless of user activity volume
2. All related data must be fetched proactively to prevent subsequent database queries during rendering
3. The system must handle users with varying levels of activity (from new users to power users)
4. Data integrity must be maintained when displaying relationships between users, posts, and comments
5. The interface must remain responsive and not degrade with increased data volume

## References

See context.md for existing user model relationships and database schema patterns used throughout the application.