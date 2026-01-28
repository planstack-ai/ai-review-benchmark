# Order Creation API with Request Validation

## Overview

The system needs to provide a REST API endpoint for creating orders that accepts order details and validates the incoming request data. The API should ensure that all required order information is properly validated before processing. This is a critical feature for data integrity and preventing invalid orders from being processed.

## Requirements

1. Create a REST controller with a POST endpoint for order creation
2. Accept a request body containing order data including customer ID, items, and addresses
3. Implement comprehensive validation for all incoming request fields using Spring validation
4. Ensure customer ID is valid and not null
5. Validate that order items are not empty and contain valid product information
6. Return appropriate HTTP status codes (201 Created for success, 400/422 for validation errors)
7. Use proper Spring Boot validation annotations (@Valid, @NotNull, @NotEmpty, etc.) to enforce data integrity
8. Handle validation errors gracefully and return structured error responses
9. Process inventory reservation and payment after validation
10. Follow Spring Boot best practices for REST controller implementation

## Constraints

1. Customer ID must be a positive number
2. Order must contain at least one item
3. Each item must have valid product ID, positive quantity, and positive unit price
4. Shipping and billing addresses are required
5. Validation should occur automatically via Spring's validation framework before business logic
6. The controller should use @Valid annotation on @RequestBody to trigger validation
7. Total amount should be calculated from order items

## References

See context.md for existing entity definitions and service implementations.