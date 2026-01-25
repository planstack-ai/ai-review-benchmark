# Order Validation with Minimum Amount

## Overview

The system validates orders before processing, checking minimum order requirements, item validity, and customer eligibility. It also calculates the total discount from various sources and ensures the order meets business requirements.

## Requirements

1. Minimum order amount is 1000 yen
2. Order must have at least one item
3. Item quantities must be greater than zero
4. Item prices cannot be negative
5. Blocked customers cannot place orders
6. Customers with overdue payments cannot place orders
7. Calculate total discount from percentage, coupon, and loyalty discounts
8. Maximum combined discount is 50% of subtotal
9. **Minimum order check must be on the final amount after discounts**
10. Return validation summary with all errors

## Constraints

1. Minimum check applies to post-discount amount, not subtotal
2. Multiple discount types can stack (within 50% cap)
3. Validation returns all errors, not just first error
4. Customer checks only apply if customer is set
5. Coupon must be active to apply coupon discount
6. Loyalty discount is 5% for loyalty members

## References

See context.md for Customer eligibility fields and discount calculation rules.
