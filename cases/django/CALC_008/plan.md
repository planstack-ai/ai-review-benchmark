# Coupon Stacking Logic Implementation

## Overview

This feature implements a coupon system for an e-commerce platform where customers can apply discount coupons to their orders. The system must enforce business rules around coupon usage to prevent abuse while providing a smooth user experience. The core business requirement is to allow only one coupon per order to maintain pricing integrity and prevent excessive discounting.

## Requirements

1. The system shall allow only one coupon to be applied per order at any given time
2. When a customer attempts to apply a new coupon, any previously applied coupon must be automatically removed from the order
3. The system shall validate that the coupon exists and is currently active before applying it
4. The system shall calculate and apply the appropriate discount amount based on the coupon's discount type and value
5. The order total must be recalculated immediately after coupon application or removal
6. The system shall provide clear feedback to the user about successful coupon application
7. The system shall handle coupon removal functionality when explicitly requested by the user
8. All coupon operations must update the order's coupon relationship in the database
9. The system shall prevent application of expired or inactive coupons
10. Discount calculations must not result in negative order totals

## Constraints

1. Coupon codes must be case-insensitive when matching
2. Only active coupons (where is_active=True) can be applied
3. Coupons must not be expired (current date must be within valid date range)
4. The final order total after discount application cannot be less than zero
5. Coupon application must be atomic - either fully successful or no changes made
6. The system must handle cases where the coupon table is empty or coupon doesn't exist

## References

See context.md for existing model definitions, view implementations, and related code structure that this feature builds upon.