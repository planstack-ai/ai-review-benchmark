# Admin Product Management Service

## Overview

Implement an admin service for managing products. Unlike the customer-facing product listings, admin views need to see ALL products including inactive ones. The service provides methods for listing products with various filters for admin dashboard purposes.

## Requirements

1. List all products regardless of active status for admin management
2. List all featured products including inactive ones for featuring management
3. List all inactive products for reactivation review
4. Support filtering by category while showing all products (active and inactive)
5. Return products sorted by most recently updated

## Constraints

1. Admin views must show inactive products - this is critical for product management
2. Do not modify the existing Product model or its scopes
3. All queries must include inactive products unless explicitly filtering by active status

## References

See context.md for Product model with existing scopes including default_scope.
