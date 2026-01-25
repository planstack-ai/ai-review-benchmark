# Minimum Order Amount Validation System

## Overview

This system implements minimum order amount validation for an e-commerce platform. The business rule requires that all orders must meet a minimum threshold of 1000 yen after all discounts have been applied. This ensures profitability and covers operational costs for order processing and fulfillment.

## Requirements

1. The system must validate that the final order total (after all discounts) meets or exceeds 1000 yen
2. Validation must occur before order confirmation and payment processing
3. If the minimum amount is not met, the system must prevent order completion
4. The system must provide clear error messaging when the minimum threshold is not satisfied
5. The minimum amount check must be performed on the discounted total, not the original subtotal
6. All discount types (percentage discounts, fixed amount discounts, coupon codes, promotional offers) must be applied before minimum amount validation
7. The system must handle multiple currencies but enforce the 1000 yen minimum for JPY transactions
8. Tax calculations should not affect the minimum order amount validation (validation occurs on pre-tax discounted amount)

## Constraints

1. The minimum order amount of 1000 yen is a fixed business rule and should not be configurable
2. Validation must handle edge cases such as orders with zero or negative totals after excessive discounts
3. The system must prevent circumvention of the minimum order requirement through order splitting or manipulation
4. Free shipping offers or shipping discounts must not count toward meeting the minimum order amount
5. Gift cards and store credit applications occur after minimum order validation
6. Partial payments or installment plans must still meet the minimum order requirement for the total order value

## References

See context.md for existing discount calculation implementations and order processing workflow details.