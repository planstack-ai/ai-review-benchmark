# Order Cancellation Authorization System

## Overview

The system manages order cancellation operations with proper authorization controls. Orders can only be cancelled by their original owner (the customer who placed the order) or by administrative users with elevated privileges. This ensures data security and prevents unauthorized modifications to order status.

## Requirements

1. Implement authorization check before allowing order cancellation operations
2. Allow order cancellation if the current user is the owner of the order
3. Allow order cancellation if the current user has administrative privileges
4. Deny order cancellation for all other users who are neither the owner nor an admin
5. Use Spring Security's @PreAuthorize annotation to enforce authorization rules
6. Validate that the order exists before performing authorization checks
7. Return appropriate HTTP status codes for unauthorized access attempts
8. Ensure the authorization logic covers all possible user scenarios

## Constraints

1. Authorization must be evaluated before any business logic execution
2. The system must handle cases where orders do not exist
3. User authentication must be verified before authorization checks
4. Administrative privileges must be clearly defined and consistently applied
5. The authorization mechanism must be stateless and not rely on session data
6. Error responses must not leak sensitive information about order ownership

## References

See context.md for existing authentication mechanisms, user role definitions, and order management service implementations.