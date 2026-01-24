# Coupon Authorization System

## Overview

The system manages promotional coupons that users can apply to their purchases. Each coupon belongs to a specific user and should only be usable by its owner. This ensures that coupons distributed to individual users (such as personalized discount codes, loyalty rewards, or targeted promotions) cannot be shared or misused by unauthorized users.

## Requirements

1. Users must be authenticated to use any coupon functionality
2. Each coupon must have an associated owner (user_id or similar identifier)
3. When a user attempts to apply a coupon, the system must verify that the coupon belongs to that user
4. Users cannot apply coupons that belong to other users
5. The system must return an appropriate error message when unauthorized coupon usage is attempted
6. Coupon ownership validation must occur before any coupon application logic
7. The authorization check must be performed on every coupon usage attempt, not cached or bypassed

## Constraints

1. Anonymous users cannot use any coupons
2. Deleted or inactive user accounts cannot use coupons
3. The ownership check must be performed at the application level, not just database constraints
4. System administrators or special roles are not exempt from coupon ownership rules
5. Coupon ownership cannot be transferred between users through the standard application flow

## References

See context.md for existing user authentication patterns and coupon model structure.