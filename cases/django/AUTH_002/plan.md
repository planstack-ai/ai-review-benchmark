# Shopping Cart Authorization Control

## Overview

This feature implements authorization controls for shopping cart operations in an e-commerce Django application. The system must ensure that users can only access and modify their own shopping carts, preventing unauthorized access to other users' cart data and purchases. This is a critical security feature that protects user privacy and prevents potential financial fraud or data breaches.

## Requirements

1. Users must only be able to view their own cart items
2. Users must only be able to add items to their own cart
3. Users must only be able to update quantities of items in their own cart
4. Users must only be able to remove items from their own cart
5. Users must only be able to clear their entire cart
6. Anonymous users must only access carts associated with their session
7. Authenticated users must only access carts associated with their user account
8. All cart operations must verify ownership before performing any modifications
9. Unauthorized access attempts must return appropriate HTTP error responses
10. Cart operations must fail gracefully when attempting to access non-existent carts

## Constraints

1. Cart ownership verification must occur before any database modifications
2. Session-based carts for anonymous users must be isolated per session
3. User-based carts must be isolated per authenticated user account
4. Cart operations must not expose cart IDs or contents of other users
5. Error messages must not reveal information about other users' carts
6. All cart endpoints must implement proper authorization checks
7. Cart data must not be accessible through URL manipulation or parameter tampering

## References

See context.md for existing cart model structure, view implementations, and URL routing patterns that this authorization system must integrate with.