# Coupon Expiry Date Validation System

## Overview

The system needs to validate coupon expiry dates to determine if a coupon is still valid for use. Coupons should remain valid through the entire expiry date, meaning a coupon that expires on a specific date should be usable until the end of that day (23:59:59). This ensures customers can use their coupons throughout the full day listed as the expiry date, providing a better user experience and meeting standard business expectations for promotional materials.

## Requirements

1. The system must accept a coupon expiry date and current datetime for comparison
2. A coupon must be considered valid if the current date is before the expiry date
3. A coupon must be considered valid if the current date is the same as the expiry date, regardless of the time of day
4. A coupon must be considered invalid if the current date is after the expiry date
5. The validation function must return a boolean value indicating coupon validity
6. The system must handle timezone-aware datetime objects correctly
7. The comparison logic must account for the full 24-hour period of the expiry date
8. The function must be reusable across different parts of the Django application

## Constraints

1. Both expiry date and current datetime parameters are required
2. The expiry date parameter must be a valid date or datetime object
3. The current datetime parameter must be a valid datetime object
4. Invalid or None parameters should raise appropriate exceptions
5. The function must handle edge cases around midnight transitions correctly
6. Timezone information must be preserved and handled consistently

## References

See context.md for existing coupon model structure and related validation patterns used in the codebase.