# Coupon Authorization System

## Overview

The system manages discount coupons that belong to specific users. Users should only be able to apply coupons that they own to their orders or transactions. This ensures proper authorization and prevents unauthorized coupon usage by other users.

## Requirements

1. Each coupon must be associated with a specific user (owner)
2. Users can only apply coupons that belong to them
3. The system must verify coupon ownership before allowing coupon usage
4. Unauthorized coupon usage attempts must be rejected with appropriate error handling
5. The coupon application process must include ownership validation as a mandatory step
6. Only authenticated users can attempt to use coupons
7. The system must prevent users from accessing or using coupons owned by other users

## Constraints

1. Coupon ownership verification must occur before any coupon value calculations
2. Anonymous users cannot use any coupons
3. Deleted or inactive user accounts cannot use coupons
4. The ownership check must be performed on every coupon usage attempt
5. Error messages should not reveal information about coupons owned by other users
6. The system must handle cases where coupon ownership data is missing or corrupted

## References

See context.md for existing model structures, authentication patterns, and related authorization implementations in the codebase.