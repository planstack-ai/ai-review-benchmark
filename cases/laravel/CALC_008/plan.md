# Coupon Application System

## Overview

The system applies discount coupons to orders. It validates coupon eligibility, calculates the discount amount based on coupon type (percentage or fixed), and updates order totals. The system tracks coupon usage and enforces usage limits.

## Requirements

1. Validate coupon is active and not expired
2. Check order meets minimum amount requirements
3. Enforce coupon usage limits
4. Support percentage discounts (e.g., 20% off)
5. Support fixed amount discounts (e.g., $10 off)
6. Fixed discounts cannot exceed order subtotal
7. Update order totals after applying discount
8. Record coupon usage for tracking
9. **Only one coupon can be applied per order** (no stacking)
10. Return appropriate error messages for validation failures

## Constraints

1. Coupon codes are case-insensitive
2. Usage limit is per-coupon, not per-user
3. Expired coupons cannot be applied
4. Inactive coupons cannot be applied
5. Order must exist and have items
6. **Coupon stacking is not allowed** - reject if order already has a coupon

## References

See context.md for Coupon model and order discount field definitions.
