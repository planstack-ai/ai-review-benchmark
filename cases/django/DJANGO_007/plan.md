# User Profile Management with Secure Database Queries

## Overview

This application provides user profile management functionality where administrators can search and filter user profiles based on various criteria. The system must handle user input securely when constructing database queries to prevent SQL injection vulnerabilities while maintaining efficient data retrieval.

## Requirements

1. Implement a user profile search endpoint that accepts search parameters via HTTP request
2. Support filtering users by username, email, and profile status fields
3. Use Django's database query methods to retrieve user profile data from the database
4. Handle dynamic search criteria where users can provide partial matches for text fields
5. Return search results in JSON format with appropriate user profile information
6. Implement proper input validation for all search parameters
7. Use parameterized queries or Django ORM methods to prevent SQL injection attacks
8. Handle empty or null search parameters gracefully without breaking the query
9. Implement case-insensitive search functionality for text-based fields
10. Ensure all user-provided input is properly sanitized before database interaction

## Constraints

1. Search parameters must be validated for appropriate data types and length limits
2. Username and email searches must support partial matching with wildcards
3. Status field must only accept predefined valid status values
4. Query results must be limited to prevent excessive resource consumption
5. All database queries must use proper escaping mechanisms for user input
6. The system must not expose sensitive user information in error messages
7. Search functionality must work with both authenticated and unauthenticated requests appropriately

## References

See context.md for existing codebase structure and related implementations.