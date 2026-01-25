# Expected Critique

## Essential Finding

The service uses floating-point arithmetic for monetary calculations, which can lead to precision errors due to how computers represent decimal numbers in binary. Operations like `0.1 + 0.2` don't equal exactly `0.3` in floating-point math, leading to accumulated errors in financial calculations.

## Key Points to Mention

1. **Bug Location**: All arithmetic operations using `float` type for monetary values, including discount calculations and tax amounts.

2. **Incorrect Logic**: Using native PHP floats for currency calculations introduces IEEE 754 floating-point representation errors. For example, `0.1 + 0.2` results in `0.30000000000000004` instead of `0.3`.

3. **Correct Implementation**: Use integer arithmetic (cents instead of dollars), PHP's BCMath extension (`bcadd`, `bcmul`), or a dedicated Money library that handles decimal precision correctly.

4. **Financial Impact**: Small precision errors accumulate over thousands of transactions, leading to discrepancies in financial reports, incorrect totals, and potential audit failures.

5. **Edge Cases**: The bug is most visible with certain decimal values (like 0.1, 0.05, 0.15) that cannot be exactly represented in binary floating-point.

## Severity Rationale

- **Accuracy Impact**: While individual errors are tiny (typically around 1e-15), they accumulate and can cause visible discrepancies in totals and reports.

- **Financial Compliance**: Financial systems require exact decimal arithmetic. Floating-point errors can cause reconciliation failures and audit issues.

- **Customer Trust**: Visible penny differences between expected and actual charges erode customer confidence.

## Acceptable Variations

- **Different Fix Approaches**: Reviews might suggest using BCMath functions, storing values as integers (cents), using a Money value object pattern, or using a library like `moneyphp/money`.

- **Terminology Variations**: The bug might be described as "IEEE 754 precision issue," "binary floating-point limitation," or "decimal representation error."

- **Impact Descriptions**: Reviews might focus on "financial calculation accuracy," "currency precision," or "rounding artifacts."
