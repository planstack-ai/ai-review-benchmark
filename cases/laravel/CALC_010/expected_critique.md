# Expected Critique

## Essential Finding

The `calculateSubtotal` method uses native PHP float multiplication (`$unitPrice * $quantity`) which can cause overflow or precision loss for very large orders. When dealing with bulk orders (e.g., 1,000,000 units × $9,999.99), this can produce incorrect results due to floating-point limitations.

## Key Points to Mention

1. **Bug Location**: The line `$total += $unitPrice * $quantity` in `calculateSubtotal` uses native PHP arithmetic that cannot safely handle extremely large values.

2. **Overflow Risk**: For very large quantities (1,000,000+) multiplied by high prices ($10,000+), the result can exceed safe integer bounds on 32-bit systems or lose precision with floats.

3. **Correct Implementation**: Use PHP's BCMath extension (`bcmul`, `bcadd`) for arbitrary precision arithmetic: `$total = bcadd($total, bcmul($unitPrice, $quantity, 2), 2)`.

4. **Business Impact**: Enterprise bulk orders with values in the billions could calculate incorrectly, leading to massive billing errors - either undercharging (revenue loss) or overcharging (customer disputes).

5. **Context Requirement**: The context.md explicitly states that calculations must "never overflow regardless of order size" and should use "string-based arithmetic (BCMath)."

## Severity Rationale

- **Critical Financial Risk**: Incorrect calculations on multi-million dollar orders could cause enormous financial discrepancies.

- **Silent Failure**: PHP won't throw an error on overflow - it will simply produce wrong numbers, making this bug hard to detect until audited.

- **Enterprise Scale**: The documented use case specifically mentions orders up to $1 billion, making this a likely scenario, not an edge case.

## Acceptable Variations

- **Different Fix Approaches**: Reviews might suggest BCMath functions, GMP extension, storing values as cents (integer), or using a Money/Decimal library.

- **Terminology Variations**: The bug might be described as "numeric overflow risk," "precision loss for large values," or "arbitrary precision needed."

- **Impact Descriptions**: Reviews might focus on "enterprise order risk," "financial calculation safety," or "large number handling."
