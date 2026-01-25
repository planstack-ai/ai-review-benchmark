# Coupon Validity Period

## Overview

Manage coupon codes with expiration dates.

## Requirements

1. Coupons have start and end dates
2. Coupon is valid on both start and end dates (inclusive)
3. Check validity at time of use
4. Support timezone-aware expiration

## Business Rules

- Coupon valid when: start_date <= current_date <= end_date
- Dates are calendar dates (not timestamps)
- A coupon expiring on Jan 31 should work all day on Jan 31
