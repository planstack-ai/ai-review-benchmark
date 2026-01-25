# Expected Critique

## Critical Bug: Reorder Logic Ignores Reserved Stock

### Location
Two locations in `ReorderService`:

1. `getProductsBelowReorderPoint()`:
```php
return Product::whereRaw('stock_quantity <= reorder_point')->get();
```

2. `calculateReorderQuantity()`:
```php
$currentStock = $product->stock_quantity;
```

### Problem
Both the reorder trigger check and quantity calculation use `stock_quantity` instead of available stock (`stock_quantity - reserved_quantity`). According to business rules:

> Reorder when: available_stock <= reorder_point

Reserved stock is committed to pending orders and should not be considered available.

### Example Scenario
- Product has:
  - `stock_quantity = 100`
  - `reserved_quantity = 90`
  - `reorder_point = 50`
  - Actually available: `100 - 90 = 10`

- Bug behavior: No reorder triggered (100 > 50)
- Correct behavior: Reorder triggered (10 <= 50)

### Impact
1. **Stockouts**: Products run out because reorder triggers too late
2. **Order delays**: Pending orders can't be fulfilled while waiting for restock
3. **Lost sales**: Customers see "out of stock" due to delayed reordering
4. **Business rule violation**: Explicitly states to use `available_stock`

### Correct Implementation

```php
private function getProductsBelowReorderPoint(): Collection
{
    return Product::whereRaw('(stock_quantity - reserved_quantity) <= reorder_point')
        ->get();
}

private function calculateReorderQuantity(Product $product): int
{
    $targetStock = ($product->daily_demand * $product->lead_time_days) + $product->safety_stock;
    $currentStock = $product->availableStock(); // Use availableStock()
    return max(0, (int) ceil($targetStock - $currentStock));
}
```

### Severity: High
Can cause systematic stockouts across product catalog when there are many pending orders.
