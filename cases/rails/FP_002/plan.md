# User Profile Management with Standard Validations

## Overview

The system requires a comprehensive user profile management feature that handles user registration, profile updates, and data integrity through standard Rails model validations. This feature ensures that user data meets business requirements and maintains data quality across the application.

## Requirements

1. Create a User model that stores essential profile information including name, email, age, and bio
2. Implement email validation to ensure proper email format and uniqueness across all users
3. Enforce presence validation for required fields (name and email)
4. Validate name length to be between 2 and 50 characters
5. Implement age validation to ensure users are between 13 and 120 years old
6. Limit bio field to maximum 500 characters when provided
7. Ensure email addresses are case-insensitive for uniqueness validation
8. Provide appropriate error messages for all validation failures
9. Handle validation errors gracefully in the user interface
10. Support both user registration and profile update workflows

## Constraints

1. Email validation must reject invalid email formats
2. Age field is optional but when provided must be within the specified range
3. Bio field is optional and can be left blank
4. Name field cannot contain only whitespace characters
5. Email uniqueness check should be performed case-insensitively
6. All validations must work consistently across create and update operations
7. System should handle edge cases like extremely long inputs gracefully

## References

See context.md for existing user management patterns and validation approaches used in the codebase.