# User Registration API with Request Validation

## Overview

The system needs to provide a REST API endpoint for user registration that accepts user details and validates the incoming request data. The API should ensure that all required user information is properly validated before processing the registration request. This is a critical security and data integrity feature that prevents invalid or malicious data from being processed by the application.

## Requirements

1. Create a REST controller with a POST endpoint at `/api/users/register` for user registration
2. Accept a request body containing user registration data including username, email, and password
3. Implement comprehensive validation for all incoming request fields
4. Ensure username is not null, not empty, and meets minimum length requirements
5. Validate email format using standard email validation rules
6. Enforce password strength requirements including minimum length and complexity
7. Return appropriate HTTP status codes for successful registration (201 Created)
8. Return validation error responses with detailed field-level error messages when validation fails
9. Use proper Spring Boot validation annotations to enforce data integrity
10. Handle validation errors gracefully and return structured error responses

## Constraints

1. Username must be at least 3 characters long and contain only alphanumeric characters
2. Email must follow standard RFC 5322 email format specification
3. Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, and one digit
4. All fields are mandatory and cannot be null or empty
5. Validation should occur before any business logic processing
6. Error responses must include field names and specific validation failure reasons
7. The API should not expose sensitive information in error messages

## References

See context.md for existing codebase structure and related implementations.