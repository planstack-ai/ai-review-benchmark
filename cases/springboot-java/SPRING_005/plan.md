# Secure Exception Handling for User Management API

## Overview

This application provides a REST API for user management operations including user registration, authentication, and profile management. The system must handle various error conditions gracefully while maintaining security best practices by preventing sensitive information disclosure through exception messages and stack traces.

## Requirements

1. All API endpoints must return consistent error response format with appropriate HTTP status codes
2. Exception messages exposed to clients must not contain sensitive system information such as database connection details, file paths, or internal service configurations
3. Stack traces must never be included in API responses sent to clients
4. Database constraint violations must be handled with user-friendly error messages that do not reveal schema details
5. Authentication and authorization failures must return generic error messages that do not indicate whether a user exists in the system
6. File system errors must be abstracted to prevent disclosure of server directory structures
7. Third-party service integration errors must be sanitized before being returned to clients
8. All exceptions must be properly logged on the server side with full details for debugging purposes
9. Custom exception classes must be used to categorize different types of business logic errors
10. Global exception handler must be implemented to ensure consistent error handling across all endpoints

## Constraints

- Error responses must maintain the same JSON structure regardless of exception type
- HTTP status codes must accurately reflect the nature of the error (4xx for client errors, 5xx for server errors)
- Sensitive operations like password reset must not reveal whether an email address exists in the system
- Rate limiting errors must not expose internal throttling mechanisms or thresholds
- Validation errors must be specific enough to help users correct input without revealing business rules

## References

See context.md for existing codebase structure and current exception handling patterns that need to be improved.