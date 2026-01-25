# Expected Critique

## Performance Bug: Inefficient Aggregation

### Location 1: `getStatistics()`
```php
$allOrders = Order::all();
$totalRevenue = $allOrders->sum('total');
$averageOrderValue = $allOrders->avg('total');
```

Loads entire orders table into memory just to sum/average. With millions of orders, this crashes the application.

### Location 2: Multiple Separate Queries
```php
$pendingOrders = Order::where('status', 'pending')->count();
$processingOrders = Order::where('status', 'processing')->count();
// ... 4 separate queries for counts
```

Each status count is a separate database query.

### Location 3: `getInventoryStats()`
```php
$products = Product::all();
$products->sum(function ($p) { return $p->price * $p->stock; });
```

Loads all products to calculate values that database can compute directly.

### Correct Implementation
```php
public function getStatistics(): array
{
    // Single query for all status counts
    $statusCounts = Order::selectRaw('status, COUNT(*) as count')
        ->groupBy('status')
        ->pluck('count', 'status');

    // Database aggregation for revenue
    $revenue = Order::selectRaw('SUM(total) as total, AVG(total) as average')
        ->first();

    // Today's orders in same query or separate indexed query
    $todayOrders = Order::whereDate('created_at', today())->count();

    return [
        'orders' => [
            'pending' => $statusCounts['pending'] ?? 0,
            // ...
        ],
        'revenue' => [
            'total' => $revenue->total ?? 0,
            'average' => $revenue->average ?? 0,
        ],
    ];
}

public function getInventoryStats(): array
{
    return Product::selectRaw('
        COUNT(*) as total_products,
        SUM(price * stock) as total_stock_value,
        SUM(CASE WHEN stock < 10 THEN 1 ELSE 0 END) as low_stock_count,
        SUM(CASE WHEN stock = 0 THEN 1 ELSE 0 END) as out_of_stock
    ')->first()->toArray();
}
```

### Severity: High
Memory exhaustion and slow queries on large datasets.
