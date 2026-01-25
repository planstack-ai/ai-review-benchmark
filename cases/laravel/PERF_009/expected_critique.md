# Expected Critique

## Performance Bug: Cache Stampede and N+1

### Location 1: Cache Stampede
```php
if (Cache::has($cacheKey)) {
    return Cache::get($cacheKey);
}
// ... expensive query ...
Cache::put($cacheKey, $result);
```

### Problem: Cache Stampede
Between `has()` and `put()`, multiple concurrent requests can all:
1. Check cache → miss
2. Query database
3. Write to cache

Under high load when cache expires: 100 concurrent requests all hit DB.

### Location 2: N+1 on Cache Miss
```php
$products->map(function ($product) {
    return [..., 'category' => $product->category->name];
});
```

On every cache miss, triggers N+1 queries for categories.

### Impact
1. **Thundering herd**: Cache expiry causes massive DB load spike
2. **Slow cache misses**: N+1 makes rebuilding cache slow
3. **No expiry**: Cache never refreshes without manual clear
4. **Cascading failures**: High load + cache miss = potential downtime

### Correct Implementation
```php
public function getProductsByCategory(int $categoryId): array
{
    $cacheKey = "products_category_{$categoryId}";

    // Atomic cache-or-compute - prevents stampede
    return Cache::remember($cacheKey, now()->addHours(1), function () use ($categoryId) {
        // Eager load to prevent N+1
        return Product::with('category')
            ->where('category_id', $categoryId)
            ->where('active', true)
            ->get()
            ->map(fn($p) => [
                'id' => $p->id,
                'name' => $p->name,
                'price' => $p->price,
                'category' => $p->category->name,
            ])
            ->toArray();
    });
}
```

For high-traffic scenarios, use cache locks:
```php
return Cache::lock($cacheKey . '_lock', 10)->block(5, function () use ($cacheKey, $categoryId) {
    return Cache::remember($cacheKey, ...);
});
```

### Severity: High
Can cause cascading failures under load.
