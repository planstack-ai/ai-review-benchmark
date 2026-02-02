# Order Creation with Mass Assignment Protection

## Overview

The system needs to handle order creation from incoming request data while maintaining proper security controls. Orders contain sensitive financial information and customer data that must be protected from unauthorized modification. The application should create orders efficiently while ensuring that only authorized fields can be mass-assigned from user input.

## Requirements

1. Create a new order record from incoming request parameters
2. Accept customer information including name, email, and phone number
3. Accept order details including product items, quantities, and pricing
4. Calculate and store the total order amount
5. Set the order status to 'pending' by default
6. Generate a unique order reference number
7. Store the order creation timestamp
8. Return the created order data upon successful creation
9. Handle validation errors appropriately
10. Protect sensitive fields from mass assignment vulnerabilities

## Constraints

1. Customer email must be in valid email format
2. Order total must be a positive decimal value
3. Product quantities must be positive integers
4. Order reference numbers must be unique across the system
5. Phone numbers should follow a standard format
6. Order status must be from a predefined set of valid statuses
7. All monetary values must be stored with appropriate precision
8. Customer name cannot be empty or null
9. At least one product item must be included in the order
10. Administrative fields should not be modifiable through mass assignment

## References

See context.md for existing model definitions, database schema, and related implementation patterns used throughout the application.