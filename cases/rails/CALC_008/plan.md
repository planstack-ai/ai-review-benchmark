# Coupon Stacking Logic Implementation

## Overview

The system needs to implement coupon application logic for e-commerce orders. Currently, the system allows multiple coupons to be applied to a single order, which creates business complications and potential revenue loss. The business requirement is to restrict orders to use only one coupon at a time, ensuring proper discount control and preventing coupon abuse.

## Requirements

1. Only one coupon shall be applied per order at any given time
2. When a new coupon is added to an order that already has a coupon, the system shall replace the existing coupon with the new one
3. The system shall calculate the total discount based on the single active coupon only
4. The system shall maintain a record of which coupon is currently applied to the order
5. The system shall validate that the applied coupon is still valid (not expired, not exceeded usage limits) before applying discounts
6. The system shall recalculate the order total whenever a coupon is added, removed, or replaced
7. The system shall provide clear feedback about which coupon is currently active on the order

## Constraints

1. Expired coupons shall not be applied to orders
2. Coupons that have reached their usage limit shall not be applied
3. The system shall handle cases where no coupon is applied (coupon field can be nil/empty)
4. Coupon codes shall be case-insensitive when matching
5. Invalid coupon codes shall be rejected with appropriate error handling
6. The discount amount shall never exceed the order subtotal
7. Percentage-based coupons shall be calculated against the order subtotal before tax

## References

See context.md for existing coupon and order model implementations that need to be modified to support single coupon logic.