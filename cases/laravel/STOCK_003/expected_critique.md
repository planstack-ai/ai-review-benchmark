# Expected Critique

## Critical Bug: Premature Stock Restoration

### Location
`processReturn()` method, line with `$product->increment('stock_quantity', $quantity)`

### Problem
Stock is restored immediately when a return is **requested**, rather than when the return is **approved** and **completed**.

### Impact
1. **Inventory inflation**: Stock appears available before item is actually received back
2. **Overselling**: Other customers may purchase items that haven't been returned yet
3. **Fraud opportunity**: Customer could request return, let others buy the "restored" stock, then cancel return
4. **Accounting discrepancy**: Physical inventory won't match system records

### Business Rule Violation
According to requirements, "Restocked items become available for sale" implies items should be physically received before becoming available.

### Correct Implementation
```php
// In processReturn() - just create the request, no stock change
$return = ReturnRequest::create([...]);

// In completeReturn() - restore stock when item is received
public function completeReturn(int $returnId): array
{
    // ... validation ...

    $product = Product::findOrFail($orderItem->product_id);
    $product->increment('stock_quantity', $return->quantity);

    // ... rest of completion logic ...
}
```

### Severity: High
This can lead to overselling and significant inventory management issues.
