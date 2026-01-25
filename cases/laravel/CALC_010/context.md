# Existing Codebase

## Expected Input Format

```php
// Order items can be provided as array of arrays
$orderItems = [
    ['unit_price' => 9999.99, 'quantity' => 100000],
    ['unit_price' => 5000.00, 'quantity' => 50000],
];

// Or as array of objects with same properties
```

## Business Rules

### Bulk Order Scenarios

Large enterprise customers may place orders with:
- Quantities up to 1,000,000 units per item
- Unit prices up to $10,000 per unit
- Total order values potentially exceeding $1 billion

### Calculation Requirements

- **Integer overflow protection**: PHP integers on 32-bit systems overflow at ~2.1 billion. Even on 64-bit systems, very large calculations should use BCMath or similar for guaranteed precision.
- Example: 1,000,000 units × $9,999.99 = $9,999,990,000 (requires 64-bit or arbitrary precision)
- All monetary calculations should use string-based arithmetic (BCMath) or convert to smallest unit (cents) with big integer handling.

### Precision Standards

Financial calculations for enterprise orders must:
1. Never lose precision due to floating-point errors
2. Never overflow regardless of order size
3. Round consistently at the final step only
