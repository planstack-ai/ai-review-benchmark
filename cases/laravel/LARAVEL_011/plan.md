# Order Access Authorization with Policy Implementation

## Overview

The system needs to implement proper authorization for order access using Laravel's policy system. Users should only be able to view, edit, or delete orders that belong to them or that they have explicit permission to access. This ensures data privacy and security by preventing unauthorized access to sensitive order information.

## Requirements

1. Create an OrderPolicy class that defines authorization rules for order operations
2. Register the OrderPolicy in the AuthServiceProvider to link it with the Order model
3. Implement policy methods for common operations: view, create, update, delete
4. Apply policy authorization in the OrderController for all relevant actions
5. Ensure that users can only access orders they own or have been granted permission to access
6. Return appropriate HTTP status codes (403 Forbidden) when authorization fails
7. Handle authorization for both authenticated and guest users appropriately
8. Implement proper error handling for authorization failures

## Constraints

1. Guest users should not have access to any order operations
2. Users must be authenticated to perform any order-related actions
3. Order ownership should be determined by the user_id field on the order model
4. Authorization checks must occur before any order data is retrieved or modified
5. Policy methods should return boolean values indicating permission status
6. All controller actions that interact with orders must use policy authorization

## References

See context.md for existing Order model structure, User model relationships, and current controller implementation patterns.