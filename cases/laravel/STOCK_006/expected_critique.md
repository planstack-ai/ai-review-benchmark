# Expected Critique

## Critical Bug: Wrong Preorder Slot Calculation

### Location
`createPreorder()` method, line:
```php
$availableSlots = $product->expected_quantity;
```

### Problem
The available preorder slots are calculated as just `expected_quantity`, ignoring existing preorders. According to the business rules:

> Preorder limit = expected_quantity - current_preorder_count

The code should be:
```php
$availableSlots = $product->expected_quantity - $product->preorder_count;
```

### Example Scenario
- Product has `expected_quantity = 100`
- Already has `preorder_count = 80`
- Actual available slots should be: `100 - 80 = 20`
- Bug allows: checking against `100` instead of `20`
- Customer requesting 50 units would be allowed (50 < 100), but only 20 slots available

### Impact
1. **Over-promising**: More preorders accepted than incoming stock can fulfill
2. **Customer disappointment**: Some preorders can never be fulfilled
3. **Inventory chaos**: preorder_count can exceed expected_quantity
4. **Business rule violation**: Directly contradicts the stated preorder limit formula

### Correct Implementation
```php
$availableSlots = $product->expected_quantity - $product->preorder_count;

if ($quantity > $availableSlots) {
    return [
        'success' => false,
        'message' => 'Requested quantity exceeds available preorder slots',
    ];
}
```

### Severity: High
Will cause preorder overselling when expected_quantity is large but most slots are already taken.
