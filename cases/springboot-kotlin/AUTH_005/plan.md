# Member Pricing Service

## Overview

This service implements pricing logic for an e-commerce platform that offers different prices for members and non-members. Members receive special discounted prices, while guests see regular prices.

## Requirements

1. Create a pricing service that returns appropriate prices based on user status
2. Members should see member-exclusive prices
3. Non-members and guests should see regular prices
4. Handle cases where user is not logged in (guest)
5. Support product-level member pricing configuration
6. Return clear price breakdown showing savings for members
7. Cache pricing data for performance
8. Log pricing requests for analytics

## Constraints

1. Member pricing only applies to logged-in members
2. Guest users must never see member prices
3. Membership status must be verified before applying discounts
4. Pricing must be consistent across all product views
5. The service should be stateless and thread-safe
6. Null user sessions indicate guest users

## References

See context.md for existing user authentication and pricing patterns in the codebase.
