# Expected Critique

## Essential Finding

The tax calculation service contains a critical bug where it uses a hardcoded tax rate of 8% (`subtotal * 0.08`) instead of the current required tax rate of 10%. This outdated tax rate will result in systematic under-collection of taxes across all orders, creating significant financial and compliance issues for the business.

## Key Points to Mention

1. **Specific Code Location**: Line in `calculate_tax_amount` method contains `subtotal * 0.08` which applies an incorrect 8% tax rate instead of the required 10% rate.

2. **Incorrect Implementation**: The hardcoded `0.08` multiplier is outdated and doesn't reflect the current tax requirements, causing all tax calculations to be 20% lower than they should be.

3. **Correct Fix**: Replace the hardcoded `0.08` with either `0.10` for the correct 10% rate, or better yet, use a configurable constant like `TaxRate.current` or similar to avoid future hardcoding issues.

4. **Business Impact**: Under-collection of taxes will result in revenue loss, potential compliance violations, and possible penalties from tax authorities due to incorrect tax remittance.

5. **Systemic Problem**: This affects every taxable order processed through the system, making it a widespread issue that compounds over time.

## Severity Rationale

- **Financial Impact**: Systematic under-collection of taxes by 20% (8% vs 10%) affects every transaction, leading to significant cumulative revenue loss and potential tax authority penalties
- **Compliance Risk**: Using incorrect tax rates violates tax regulations and could result in audits, fines, and legal complications for the business
- **Widespread Scope**: This bug affects all orders processed through the system, making it a critical issue that impacts the entire customer base and all financial reporting

## Acceptable Variations

- **Alternative Descriptions**: Could be described as "outdated tax rate," "incorrect tax percentage," or "stale tax calculation constant" - all referring to the same core issue of using 8% instead of 10%
- **Different Fix Approaches**: Reviewers might suggest various solutions like configuration files, database-stored rates, or environment variables, all of which would be valid alternatives to hardcoding
- **Impact Framing**: Some reviewers might focus more on the compliance aspect while others emphasize the financial loss - both perspectives are valid for describing the severity