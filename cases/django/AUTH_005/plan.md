# Guest Member Pricing System

## Overview

The system needs to implement a pricing structure where logged-in members receive special pricing on products, while guest users (non-authenticated visitors) see standard pricing. This feature ensures that membership benefits are properly restricted to authenticated users only, encouraging user registration and login while maintaining clear pricing transparency.

## Requirements

1. Display member pricing only to authenticated users who are logged in
2. Display standard/guest pricing to all non-authenticated visitors
3. Ensure pricing information is fetched based on the user's authentication status
4. Maintain consistent pricing display across all product views and listings
5. Prevent any exposure of member pricing data to guest users through any interface
6. Handle user session changes appropriately when switching between guest and member states
7. Apply member pricing automatically upon user login without requiring page refresh
8. Ensure member pricing is immediately hidden when user logs out

## Constraints

1. Member pricing must never be visible in page source, API responses, or browser developer tools for guest users
2. Price calculations must be performed server-side to prevent client-side manipulation
3. Guest users attempting to access member-only pricing endpoints should receive appropriate error responses
4. System must gracefully handle edge cases where user authentication status changes during browsing session
5. All pricing-related database queries must include proper authentication checks
6. Member pricing data must not be cached in a way that could leak to guest users

## References

See context.md for existing authentication patterns, user model structure, and current pricing implementation details.