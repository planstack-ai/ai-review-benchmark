# Database Query Performance Optimization Plan

## Overview

This feature implements a user search functionality that allows filtering users by their email domain and account status. The system needs to efficiently handle queries against a users table that contains thousands of records. Users should be able to search for active users within specific email domains (e.g., all active users with @company.com emails) with fast response times.

## Requirements

1. Create a database migration that adds appropriate indexes to the users table for email and status columns
2. Implement a User model method that filters users by email domain pattern matching
3. Implement a User model method that filters users by account status
4. Create a combined search method that filters users by both email domain and status simultaneously
5. Ensure all database queries utilize the created indexes for optimal performance
6. The search functionality must handle case-insensitive email domain matching
7. Return results in a consistent order (alphabetical by email)
8. Handle empty or nil search parameters gracefully by returning appropriate default results

## Constraints

1. Email domain matching must support partial matches (e.g., searching for "company" should match "@company.com", "@company.org")
2. Status filtering must only accept valid status values: "active", "inactive", "pending"
3. The combined search must return an empty collection when no matches are found
4. Query performance must remain efficient even with large datasets (10,000+ user records)
5. All database queries must be SQL injection safe

## References

See context.md for existing database schema and model structure details.