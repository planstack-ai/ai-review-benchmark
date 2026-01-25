# Expected Critique

## Essential Finding

The service does not check if the order already has a coupon applied before applying a new one. This allows customers to apply multiple coupons to the same order, violating the single-coupon policy and potentially giving excessive discounts.

## Key Points to Mention

1. **Bug Location**: The `apply` method lacks a check for existing coupons before calling `applyCouponDiscount`.

2. **Missing Validation**: The Order model has a `hasCouponApplied()` method that is never called. The service should check this before allowing a new coupon.

3. **Correct Implementation**: Add validation at the start of `apply()`: `if ($this->order->hasCouponApplied()) { return $this->failure('Order already has a coupon applied'); }`

4. **Business Impact**: Customers can stack multiple coupons for compounding discounts (e.g., 20% + 20% = 36% off), leading to significant revenue loss.

5. **Exploit Potential**: Malicious users could repeatedly call the coupon endpoint to stack discounts, potentially getting items for free or negative amounts.

## Severity Rationale

- **Financial Impact**: Coupon stacking can lead to extreme discounts far beyond intended promotions, causing direct revenue loss.

- **Policy Violation**: The business explicitly requires single-coupon policy, and this implementation directly contradicts that requirement.

- **Abuse Vector**: Once discovered, this vulnerability can be easily exploited by customers or malicious actors.

## Acceptable Variations

- **Different Fix Approaches**: Reviews might suggest checking `coupon_discount > 0`, checking the `appliedCoupons` relationship count, or adding a database constraint.

- **Terminology Variations**: The bug might be described as "missing stacking prevention," "coupon accumulation allowed," or "multiple discount vulnerability."

- **Impact Descriptions**: Reviews might focus on "revenue leakage," "discount abuse," or "business rule violation."
