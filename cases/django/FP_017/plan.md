# Optimized Batch Insert for User Registration System

## Overview

The system needs to handle bulk user registration scenarios efficiently, such as importing users from CSV files, batch enrollment from external systems, or mass user creation during organizational onboarding. The current implementation processes users one by one, which creates performance bottlenecks when dealing with large datasets. This feature implements optimized batch insertion to significantly reduce database round trips and improve throughput for bulk operations.

## Requirements

1. Implement a bulk user creation endpoint that accepts a list of user data objects
2. Use Django's bulk_create() method to insert multiple users in a single database transaction
3. Validate all user data before performing the bulk insert operation
4. Return appropriate HTTP status codes: 201 for successful bulk creation, 400 for validation errors
5. Include proper error handling that rolls back the entire batch if any individual user fails validation
6. Support batch sizes up to 1000 users per request to prevent memory issues
7. Return a JSON response containing the count of successfully created users
8. Ensure all created users have properly set timestamps (created_at, updated_at)
9. Handle duplicate email addresses gracefully by skipping duplicates and continuing with valid entries
10. Log bulk operations for audit purposes including batch size and execution time

## Constraints

1. Email addresses must be unique across all users in the system
2. Each user record must include required fields: email, first_name, last_name
3. Email addresses must follow standard email format validation
4. Names must not exceed 150 characters each
5. Batch size cannot exceed 1000 users to prevent memory exhaustion
6. Empty batches should return appropriate error response
7. Malformed JSON requests should return 400 status with descriptive error message
8. Database constraints must be respected (foreign key relationships, field lengths)

## References

See context.md for existing user model structure and current single-user creation implementation patterns.