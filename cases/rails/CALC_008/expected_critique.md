# Expected Critique

## Essential Finding

The code allows multiple coupons to be stacked on a single order by appending to the `applied_coupons` array without checking if a coupon is already applied. This violates the business requirement of allowing only one coupon per order and can lead to excessive discounts and revenue loss.

## Key Points to Mention

1. **Code Location**: The bug is in the `apply_coupon_discount` method at line `order.applied_coupons << coupon` where coupons are appended to an array without validation.

2. **Current Implementation Problem**: The service appends new coupons to the `applied_coupons` collection without checking if any coupon is already applied to the order, enabling coupon stacking.

3. **Correct Fix**: Add validation to check if a coupon is already applied before applying a new one, either by returning early with an error or replacing the existing coupon with the new one.

4. **Business Impact**: Multiple coupons can compound discounts beyond intended limits, potentially resulting in orders with excessive discounts or even negative totals, causing significant revenue loss.

5. **Missing Validation**: The service lacks any check for existing coupons in the validation chain at the beginning of the `call` method, allowing the stacking behavior to proceed unchecked.

## Severity Rationale

- **Direct Revenue Impact**: Coupon stacking can result in discounts exceeding 100% of order value, leading to immediate financial losses on every affected order
- **System-Wide Vulnerability**: This affects all orders using the coupon system, making it a critical business logic flaw rather than an edge case
- **Exploitation Potential**: Customers can deliberately abuse this functionality to obtain products at heavily discounted or negative prices

## Acceptable Variations

- **Prevention vs Replacement Approach**: Reviews may suggest either preventing multiple coupons entirely or implementing coupon replacement logic where new coupons override existing ones
- **Validation Location**: The fix could be implemented either as early validation in the `call` method or as a check within `apply_coupon_discount` before appending to the collection
- **Error Handling Variations**: Solutions may vary in how they handle the multiple coupon scenario - returning an error, silently replacing, or providing user choice