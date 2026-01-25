# Expected Critique

## Essential Finding

The `calculateBasePoints` method calculates points based on `$this->order->subtotal` (pre-discount amount) instead of `$this->order->total` (post-discount amount). This gives customers more points than they should earn based on the actual amount paid.

## Key Points to Mention

1. **Bug Location**: The `calculateBasePoints` method uses `$this->order->subtotal * $pointRate` instead of using the discounted total.

2. **Incorrect Logic**: Points should be earned on the amount actually paid. If a customer has a $100 order with a $20 discount, they should earn points on $80, not $100.

3. **Correct Implementation**: Replace `$this->order->subtotal` with `$this->order->total` in the base points calculation to use the post-discount amount.

4. **Business Impact**: Customers earn inflated points, which increases the company's loyalty point liability and can be exploited by using large discounts to earn disproportionate rewards.

5. **Inconsistency**: The code already uses `$this->order->total` for other checks (minimum purchase, $100 bonus threshold), making the use of `subtotal` inconsistent.

## Severity Rationale

- **Financial Impact**: Over-awarding points creates a liability that the company must honor when customers redeem points.

- **Abuse Potential**: Customers could exploit this by using discount codes to earn more points than the actual value of their purchase.

- **Business Logic Error**: The implementation contradicts the documented business rule that points should be based on "the actual amount paid."

## Acceptable Variations

- **Different Fix Approaches**: The fix is straightforward - use `total` instead of `subtotal`. Some reviews might also suggest renaming variables for clarity.

- **Terminology Variations**: The bug might be described as "using gross instead of net," "pre-discount vs post-discount error," or "wrong order amount used."

- **Impact Descriptions**: Reviews might focus on "point inflation," "loyalty program abuse," or "calculation basis error."
