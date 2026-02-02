# Coupon Application Service

## Overview

This service implements a coupon application system for an e-commerce platform. Customers can apply discount coupons to their orders. The system enforces a single coupon per order policy to maintain pricing integrity.

## Requirements

1. Create a coupon application service that validates and applies coupons to orders
2. Enforce single coupon per order policy - only one coupon can be applied
3. Validate coupon code exists and is not expired
4. Validate coupon minimum order amount requirements
5. Calculate discount amount based on coupon type (percentage or fixed amount)
6. Update order with applied coupon information
7. Return clear error messages for invalid coupon applications
8. Support coupon usage tracking for single-use coupons

## Constraints

1. Only one coupon can be applied per order
2. Coupons cannot be applied to orders below minimum amount threshold
3. Expired coupons must be rejected
4. Single-use coupons cannot be reused
5. The service should be stateless and thread-safe
6. Coupon discounts cannot exceed order total

## References

See context.md for existing coupon entities and validation patterns in the codebase.
