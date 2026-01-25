# Expected Critique

## Essential Finding

The `calculateSubtotal` method rounds each item's subtotal before summing, which can lead to accumulated rounding errors. When dealing with many items, the difference between "round then sum" and "sum then round" can be significant, causing discrepancies in order totals.

## Key Points to Mention

1. **Bug Location**: The `calculateSubtotal` method uses `round($this->calculateItemSubtotal($item), 2)` inside the sum, rounding each item individually.

2. **Incorrect Logic**: Rounding each item's subtotal before summing introduces cumulative rounding errors. For example, three items at $1.333 each would become $1.33 × 3 = $3.99 instead of the correct $4.00.

3. **Correct Implementation**: The subtotal should be calculated by summing all item totals first, then rounding the final result: `round($this->order->orderItems->sum(...), 2)`.

4. **Financial Impact**: Over many transactions, the accumulated rounding differences can result in significant discrepancies between calculated and expected totals.

5. **Accounting Compliance**: Inconsistent rounding can cause issues with financial audits and reconciliation, as the sum of line items may not match the order total.

## Severity Rationale

- **Accuracy Impact**: While individual differences are small (typically under a cent per item), they accumulate across large orders and many transactions.

- **Audit Risk**: Financial systems expect consistent calculations. Discrepancies between line item sums and order totals raise red flags during audits.

- **Customer Trust**: Visible discrepancies in receipts or invoices can undermine customer confidence.

## Acceptable Variations

- **Different Fix Approaches**: The fix could involve removing the per-item rounding and only rounding the final sum, or using a higher precision during intermediate calculations.

- **Terminology Variations**: The bug might be described as "premature rounding," "rounding accumulation error," or "incorrect rounding strategy."

- **Impact Descriptions**: Reviews might focus on "penny differences," "rounding discrepancies," or "calculation precision issues."
