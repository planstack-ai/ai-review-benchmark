# Coupon Redemption Service

## Overview

This service implements coupon redemption logic for an e-commerce platform. Users receive personal coupons tied to their account and should only be able to use their own coupons.

## Requirements

1. Create a coupon redemption service that validates coupon ownership
2. Users can only redeem coupons assigned to their account
3. Validate coupon code exists and belongs to the requesting user
4. Check coupon expiration and usage status
5. Apply coupon discount to order
6. Mark coupon as used after successful redemption
7. Return clear error messages for invalid redemptions
8. Support various coupon types (percentage, fixed amount)

## Constraints

1. Coupons are user-specific and non-transferable
2. Users cannot use coupons assigned to other users
3. Coupon ownership must be verified before redemption
4. Each coupon can only be used once
5. The service should be stateless and thread-safe
6. Expired coupons cannot be redeemed

## References

See context.md for existing coupon entities and user authentication patterns in the codebase.
