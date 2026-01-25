# Expected Critique

## Performance Bug: N+1 Query Problem

### Location
`getActiveProducts()` and `getProductsByCategory()` methods:
```php
$products = Product::where('active', true)->paginate($perPage);
// ...
foreach ($products as $product) {
    $result[] = [
        'category_name' => $product->category->name, // Query per iteration!
    ];
}
```

### Problem
The category relationship is accessed inside the loop, but no eager loading is used. This causes:
- 1 query to fetch products
- N queries to fetch categories (one per product)

For 20 products per page: 21 queries instead of 2.

### Impact
1. **Database load**: Linear increase in queries with page size
2. **Response time**: Each query adds latency
3. **Resource waste**: Database connections, memory for query parsing
4. **Scalability issues**: Gets worse as data grows

### Correct Implementation
```php
public function getActiveProducts(int $perPage = 20): array
{
    $products = Product::with('category') // Eager load!
        ->where('active', true)
        ->orderBy('created_at', 'desc')
        ->paginate($perPage);

    // Now category is already loaded, no additional queries
    // ...
}
```

Or use `select` with join if only needing specific fields:
```php
$products = Product::select('products.*', 'categories.name as category_name')
    ->join('categories', 'products.category_id', '=', 'categories.id')
    ->where('products.active', true)
    ->paginate($perPage);
```

### Severity: Medium
Common performance issue that scales poorly with data size.
