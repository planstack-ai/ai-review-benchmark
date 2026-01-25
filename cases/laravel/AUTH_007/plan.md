# Coupon Redemption System

## Overview

The system allows users to redeem discount coupons on their orders. It validates coupon eligibility, calculates the discount amount, and tracks usage. Some coupons are user-specific and should only be redeemable by their assigned owners.

## Requirements

1. Validate coupon code exists and is active
2. Check coupon has not expired
3. Verify usage limit not exceeded
4. Check order meets minimum amount
5. Calculate discount (percentage or fixed)
6. Cap percentage discounts at max_discount_amount if set
7. Record coupon usage
8. **User-specific coupons can only be used by their assigned owner**

## Constraints

1. Coupon codes are case-insensitive
2. Global coupons (user_id = null) can be used by anyone
3. User-specific coupons (user_id set) can only be used by that user
4. Discount cannot exceed order total
5. Usage tracking is per coupon, not per user

## References

See context.md for Coupon ownership model and user assignment.
