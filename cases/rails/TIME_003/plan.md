# Coupon Expiry Date Validation System

## Overview

The system needs to validate whether coupons are still valid based on their expiry dates. Coupons should remain valid through the entire day of their expiry date, not just until the moment they were created. This ensures customers can use coupons throughout the business day on the expiry date itself.

## Requirements

1. The system must determine if a coupon is valid based on its expiry date
2. A coupon must be considered valid on its expiry date until the end of that day (23:59:59)
3. A coupon must be considered invalid starting from the beginning of the day after its expiry date
4. The validation must work correctly across different time zones
5. The system must handle edge cases where the current time is exactly at midnight on the expiry date
6. The validation logic must return a boolean result indicating coupon validity
7. The system must properly handle date-only expiry values without time components

## Constraints

1. Expiry dates may be stored as Date objects without time information
2. Current time comparisons must account for the full day duration of the expiry date
3. The system must not invalidate coupons prematurely within the expiry date
4. Time zone handling must be consistent between expiry date and current time comparisons

## References

See context.md for existing coupon model implementations and related time handling patterns in the codebase.