# Expected Critique

## Performance Bug: Individual Operations in Loop

### Location
Multiple methods with the same pattern:
```php
foreach ($priceUpdates as $update) {
    $product = Product::find($update['product_id']); // N SELECTs
    $product->update(['price' => ...]); // N UPDATEs
    PriceHistory::create([...]); // N INSERTs
}
```

### Problem
For 1000 price updates: 1000 + 1000 + 1000 = **3000 queries**
Could be done in **3 queries**.

### Impact
1. **Extreme slowness**: Linear time with batch size
2. **Connection overhead**: Each query has round-trip latency
3. **Lock contention**: Many small transactions
4. **Timeout risk**: Large batches fail

### Correct Implementations

For `updatePrices()`:
```php
public function updatePrices(array $priceUpdates): array
{
    $productIds = array_column($priceUpdates, 'product_id');
    $products = Product::whereIn('id', $productIds)->get()->keyBy('id');

    $histories = [];

    DB::transaction(function () use ($priceUpdates, $products, &$histories) {
        foreach ($priceUpdates as $update) {
            $product = $products[$update['product_id']] ?? null;
            if ($product) {
                $histories[] = [
                    'product_id' => $product->id,
                    'old_price' => $product->price,
                    'new_price' => $update['new_price'],
                    'created_at' => now(),
                    'updated_at' => now(),
                ];
            }
        }

        // Bulk update using CASE WHEN
        // Or use upsert() in Laravel 8+
    });

    PriceHistory::insert($histories);
}
```

For `deactivateProducts()`:
```php
public function deactivateProducts(array $productIds): int
{
    return Product::whereIn('id', $productIds)
        ->where('active', true)
        ->update(['active' => false]);
}
```

For `bulkPriceIncrease()`:
```php
public function bulkPriceIncrease(float $percentage): int
{
    return Product::where('active', true)
        ->update(['price' => DB::raw("ROUND(price * (1 + {$percentage} / 100), 2)")]);
}
```

### Severity: High
Batch operations become unusable at scale.
