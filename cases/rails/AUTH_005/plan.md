# Guest Member Pricing Authorization System

## Overview

The system needs to implement member-specific pricing that is only available to authenticated users. Guest users (non-logged-in visitors) should see standard pricing, while logged-in members should see discounted member pricing. This feature ensures that pricing benefits are restricted to verified members only.

## Requirements

1. Display standard pricing to all guest (unauthenticated) users
2. Display member pricing to authenticated users only
3. Verify user authentication status before applying member pricing
4. Ensure pricing information is not exposed to unauthorized users through any means
5. Maintain consistent pricing display across all product views
6. Handle authentication state changes appropriately (login/logout scenarios)
7. Prevent client-side manipulation of pricing information
8. Apply member pricing automatically upon successful authentication
9. Revert to standard pricing immediately upon logout
10. Ensure member pricing is only calculated and displayed server-side

## Constraints

1. Member pricing must never be visible or accessible to guest users
2. Authentication status must be verified on each request involving pricing
3. Pricing calculations must occur server-side only
4. No pricing information should be cached for unauthenticated sessions
5. Member pricing data must not be included in responses to guest users
6. System must handle edge cases where authentication status is ambiguous
7. Pricing display must be consistent across page refreshes and navigation

## References

See context.md for existing authentication patterns and pricing model implementations in the codebase.