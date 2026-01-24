# Minimum Order Amount Validation

## Overview

The system must enforce a minimum order amount of 1000 yen to ensure order profitability and reduce processing costs for small transactions. This validation should occur after all discounts have been applied to determine the final order total that the customer will pay.

## Requirements

1. The system must validate that the final order amount (after all discounts) meets the minimum threshold of 1000 yen
2. The validation must be performed before order confirmation or payment processing
3. If the order amount falls below the minimum threshold, the system must reject the order with an appropriate error message
4. The minimum amount check must use the discounted total, not the original subtotal
5. The system must clearly communicate the minimum order requirement to users when validation fails
6. The validation must handle edge cases where the order total equals exactly 1000 yen (should be accepted)

## Constraints

1. The minimum order amount is fixed at 1000 yen and should not be configurable
2. Validation must occur after discount calculations are complete
3. Free shipping promotions or other non-monetary benefits do not count toward the minimum amount
4. Tax calculations should not affect the minimum order validation (validate against pre-tax discounted amount)
5. The system must handle decimal precision correctly when comparing amounts

## References

See context.md for existing discount calculation implementations and order processing flow.