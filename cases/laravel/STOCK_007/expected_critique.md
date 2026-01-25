# Expected Critique

## Critical Bug: Transfer Ignores Reserved Stock

### Location
`initiateTransfer()` method, line:
```php
if ($sourceStock->quantity < $quantity) {
```

### Problem
The transfer availability check uses `quantity` (total stock) instead of `availableQuantity()` (stock minus reserved). This violates the business rule:

> Source warehouse must have available (non-reserved) stock

### Example Scenario
- Warehouse A has product with:
  - `quantity = 100`
  - `reserved_quantity = 80` (for pending orders)
  - `availableQuantity() = 20`
- Transfer request for 50 units
- Bug: Check passes (50 < 100)
- Reality: Only 20 units are available, 80 are reserved for customer orders

### Impact
1. **Order fulfillment failure**: Reserved stock transferred away, orders can't be fulfilled
2. **Customer orders cancelled**: Stock no longer available at source warehouse
3. **Business rule violation**: Explicitly states reserved stock should not be transferable
4. **Inventory integrity**: Creates inconsistent state between reservations and actual stock

### Correct Implementation
```php
if ($sourceStock->availableQuantity() < $quantity) {
    return [
        'success' => false,
        'message' => 'Insufficient available stock in source warehouse',
    ];
}
```

### Secondary Issue
The `shipTransfer()` method doesn't re-verify stock availability before deducting. If stock was consumed between initiation and shipping, the transfer could cause negative stock.

### Severity: High
Can directly cause order fulfillment failures when reserved stock is transferred.
