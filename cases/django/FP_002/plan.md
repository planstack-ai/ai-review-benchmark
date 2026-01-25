# User Profile Management with Standard Django Model Validation

## Overview

This system manages user profiles with comprehensive data validation to ensure data integrity and user experience quality. The application handles user registration, profile updates, and maintains consistent data standards across all user interactions. Standard Django model validation mechanisms are employed to enforce business rules and data constraints at the model level.

## Requirements

1. Create a UserProfile model that extends or relates to Django's User model
2. Implement email validation to ensure proper email format and uniqueness
3. Enforce username constraints including minimum length, maximum length, and allowed characters
4. Validate age field to ensure users meet minimum age requirements and reasonable maximum limits
5. Implement phone number validation with proper format checking
6. Create bio field validation with appropriate length constraints
7. Ensure all validation errors provide clear, user-friendly messages
8. Implement model-level validation using Django's built-in validation framework
9. Handle validation for both create and update operations consistently
10. Provide appropriate default values where applicable
11. Ensure all required fields are properly marked and validated
12. Implement proper string representation methods for model instances

## Constraints

1. Email addresses must be unique across all user profiles
2. Username must be between 3 and 30 characters and contain only alphanumeric characters and underscores
3. Age must be between 13 and 120 years inclusive
4. Phone numbers must follow a standard format pattern
5. Bio field must not exceed 500 characters
6. All validation must occur at the model level using Django's validation system
7. Validation errors must be descriptive and actionable for end users
8. The system must handle edge cases gracefully without raising unhandled exceptions

## References

See context.md for existing codebase structure and related implementations.