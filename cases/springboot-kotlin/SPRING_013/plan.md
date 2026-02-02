# SPRING_013: Validate nested request objects

## Overview

Implement order creation endpoint with comprehensive input validation for the order request including nested order items.

## Requirements

1. Validate customer email is not blank
2. Validate order items list is not empty
3. Validate each order item:
   - Product name is not blank
   - Quantity is positive
   - Price is positive
4. Return 400 Bad Request with validation errors if any validation fails

## Constraints

- Use Spring Boot validation annotations (@Valid, @NotBlank, @Positive, etc.)
- All validation should happen before business logic execution
- Nested objects must be validated recursively
- Controller should use @Valid annotation on request body

## References

- Spring Boot Validation documentation
- JSR 380 Bean Validation
- Hibernate Validator
