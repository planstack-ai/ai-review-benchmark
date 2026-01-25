# Expected Critique

## Essential Finding

The `validateMinimumAmount` method checks the subtotal against the minimum order amount, but the business rule requires checking the **final amount after discounts**. This allows orders below the minimum threshold to pass validation when discounts are applied.

## Key Points to Mention

1. **Bug Location**: The `validateMinimumAmount` method uses `$subtotal < self::MINIMUM_ORDER_AMOUNT` but should use the post-discount total.

2. **Incorrect Logic**: An order with 1500 yen subtotal and 600 yen in discounts has a final amount of 900 yen, which is below the 1000 yen minimum. But this validation would pass because it only checks the subtotal.

3. **Correct Implementation**: Replace the check with `$this->calculateOrderTotal() < self::MINIMUM_ORDER_AMOUNT` to validate against the discounted amount.

4. **Business Impact**: Orders below the minimum profitable threshold can slip through, leading to unprofitable transactions especially when combined with shipping costs.

5. **Inconsistency**: The class already has `calculateTotalDiscount()` and `calculateOrderTotal()` methods, making it clear the intent was to check the final amount.

## Severity Rationale

- **Financial Impact**: Orders below minimum thresholds may not cover operational costs (shipping, handling, payment processing), making them unprofitable.

- **Business Rule Violation**: The minimum order policy exists for a reason - to ensure profitability. This bug undermines that policy.

- **Exploitation Risk**: Customers could use large discount codes to place very small orders that the business cannot profitably fulfill.

## Acceptable Variations

- **Different Fix Approaches**: Reviews might suggest using `calculateOrderTotal()` directly, or passing the discounted amount as a parameter.

- **Terminology Variations**: The bug might be described as "validation on wrong amount," "pre-discount validation error," or "minimum threshold bypass."

- **Impact Descriptions**: Reviews might focus on "profitability risk," "minimum order bypass," or "policy circumvention."
