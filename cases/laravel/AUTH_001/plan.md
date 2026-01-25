# Order Access Authorization System

## Overview

The system manages customer orders in an e-commerce platform where users must be authenticated and authorized to view order information. Each order belongs to a specific user, and the system must enforce strict access controls to ensure users can only access their own order data. This is critical for maintaining customer privacy and data security compliance.

## Requirements

1. Users must be authenticated before accessing any order information
2. Users can only view orders that belong to their own user account
3. When a user attempts to access an order, the system must verify the order's user_id matches the current user's ID
4. If a user attempts to access another user's order, the system must deny access with an appropriate error response
5. The system must return a 404 Not Found response when users attempt to access orders that don't belong to them
6. All order access attempts must be logged for security auditing purposes
7. The authorization check must occur before any order data is retrieved or processed
8. Guest users (non-authenticated) must be redirected to login before any order access

## Constraints

1. Order IDs may be sequential or predictable, making unauthorized access attempts possible
2. The system must not reveal whether an order exists when denying access to unauthorized users
3. Authorization checks must be performed on every request, not cached
4. The user-order relationship is established through the orders.user_id foreign key
5. System must handle edge cases where orders exist but users have been deleted
6. Performance impact of authorization checks must be minimized through efficient database queries

## References

See context.md for existing authentication middleware, user model structure, and order model relationships that should be leveraged in the implementation.
