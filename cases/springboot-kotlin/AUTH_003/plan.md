# Order Cancellation Authorization System

## Overview

The system manages order cancellation operations with proper authorization controls. Orders can only be cancelled by their original owner (the customer who placed the order) or by administrative users with elevated privileges. This ensures data security and prevents unauthorized modifications to order status.

## Requirements

1. Implement endpoint for order cancellation that accepts an order ID parameter
2. Verify the authenticated user's identity before processing cancellation requests
3. Allow order cancellation if the requesting user is the original order owner
4. Allow order cancellation if the requesting user has administrative privileges
5. Deny cancellation requests from users who are neither the order owner nor administrators
6. Return appropriate HTTP status codes for authorized and unauthorized requests
7. Include proper error messages for unauthorized access attempts
8. Ensure order ownership is determined by comparing user IDs between the authenticated user and the order's customer
9. Administrative privileges should be determined by checking user roles or permissions
10. Apply authorization checks before any order modification logic

## Constraints

1. Authentication must be verified before authorization checks
2. Order must exist in the system before authorization validation
3. Cancelled orders cannot be cancelled again
4. Authorization logic must handle null or missing user information gracefully
5. Role-based access control must be consistently applied across the application
6. User identity comparison must be exact and case-sensitive
7. Administrative role verification must check against predefined role constants or enums

## References

See context.md for existing authentication mechanisms, user role definitions, and order entity structure that should be leveraged in this implementation.