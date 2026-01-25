# Coupon Stacking Logic Implementation

## Overview

This feature implements a coupon system for an e-commerce platform where customers can apply discount coupons to their orders. The system must enforce business rules around coupon usage to prevent abuse while providing a smooth customer experience. The core business requirement is to allow only one coupon per order to maintain pricing integrity and prevent excessive discounting.

## Requirements

1. The system shall allow customers to apply exactly one coupon per order
2. When a customer attempts to apply a coupon, the system shall validate that no other coupon is currently applied to the order
3. If a coupon is already applied and the customer attempts to apply a different coupon, the system shall replace the existing coupon with the new one
4. The system shall calculate and apply the discount amount based on the active coupon's discount rules
5. The system shall update the order total to reflect the coupon discount
6. The system shall provide clear feedback to the customer about coupon application success or failure
7. The system shall maintain an audit trail of coupon applications and removals for each order
8. The system shall validate coupon eligibility before application (expiration date, usage limits, minimum order requirements)

## Constraints

1. Only active, non-expired coupons may be applied to orders
2. Coupons cannot be applied to orders that have already been completed or shipped
3. The discount amount cannot exceed the order subtotal
4. Percentage-based coupons must be calculated against the order subtotal before taxes
5. Fixed-amount coupons must be applied as absolute values in the order currency
6. The system must handle concurrent coupon applications gracefully to prevent race conditions
7. Coupon codes are case-insensitive for user convenience
8. Each coupon can only be used once per customer if it has single-use restrictions

## References

See context.md for existing model definitions, database schema, and related implementation patterns used in the current codebase.