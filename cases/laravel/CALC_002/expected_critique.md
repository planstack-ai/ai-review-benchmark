# Expected Critique

## Essential Finding

The `calculateTotal` method applies tax to the subtotal before subtracting the discount, which violates standard tax calculation rules. Tax should be calculated on the discounted amount (subtotal minus discount), not on the original subtotal. This results in customers paying more tax than they should.

## Key Points to Mention

1. **Bug Location**: The `calculateTotal` method calculates `taxedSubtotal() - discountAmount`, which applies tax before discount instead of after.

2. **Incorrect Logic**: The current flow is: subtotal → apply tax → subtract discount. The correct flow should be: subtotal → subtract discount → apply tax.

3. **Correct Implementation**: The total should be calculated as `($this->subtotal - $this->discountAmount) * (1 + self::TAX_RATE)` to apply tax only on the discounted amount.

4. **Financial Impact**: Customers are overcharged on tax because tax is calculated on the full amount before discount. For example, on a $100 order with a $20 discount, customers pay tax on $100 instead of $80.

5. **Legal/Compliance Risk**: In most jurisdictions, sales tax must be calculated on the actual sale price after discounts. This implementation could result in tax compliance issues.

## Severity Rationale

- **Financial Impact**: Customers are systematically overcharged on tax, leading to customer complaints and potential refund requests.

- **Legal Risk**: Incorrect tax calculation may violate tax regulations in many jurisdictions, potentially resulting in penalties or audits.

- **Trust Impact**: When customers notice they're paying tax on undiscounted amounts, it damages trust and brand reputation.

## Acceptable Variations

- **Different Fix Approaches**: The fix could be implemented by changing the order of operations in `calculateTotal`, or by modifying `taxableAmount` to return the discounted subtotal.

- **Terminology Variations**: The bug might be described as "tax applied to gross instead of net," "incorrect tax base," or "tax calculation sequence error."

- **Impact Descriptions**: Reviews might focus on "customer overcharge," "tax compliance violation," or "incorrect order of operations."
