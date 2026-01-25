# Expected Critique

## Performance Bug: Memory Exhaustion on Export

### Location
`exportOrders()` and `exportAllUsers()`:
```php
$orders = Order::with('user')
    ->whereBetween('created_at', [$startDate, $endDate])
    ->get(); // Loads everything into memory
```

### Problem
Loading all matching records into memory before processing. For large datasets:
- 1 million orders × ~500 bytes = ~500MB just for data
- Plus Eloquent model overhead (~2x-3x)
- Plus string concatenation creating copies
- Result: Memory exhaustion, process killed

### Impact
1. **Memory exhaustion**: `Allowed memory size exhausted` errors
2. **Server instability**: OOM killer terminates process
3. **Failed exports**: Large date ranges always fail
4. **User frustration**: Export feature unusable

### Correct Implementation
```php
public function exportOrders(string $startDate, string $endDate): string
{
    $filename = "orders_export_" . now()->format('Y-m-d_H-i-s') . ".csv";
    $path = storage_path("app/exports/{$filename}");

    $handle = fopen($path, 'w');
    fputcsv($handle, ['ID', 'Customer Name', 'Customer Email', 'Total', 'Status', 'Created At']);

    // Use cursor for memory-efficient iteration
    Order::with('user')
        ->whereBetween('created_at', [$startDate, $endDate])
        ->cursor()
        ->each(function ($order) use ($handle) {
            fputcsv($handle, [
                $order->id,
                $order->user->name,
                $order->user->email,
                $order->total,
                $order->status,
                $order->created_at->toISOString(),
            ]);
        });

    fclose($handle);

    return $filename;
}
```

Or use chunk() for batch processing:
```php
Order::with('user')
    ->whereBetween(...)
    ->chunk(1000, function ($orders) use ($handle) {
        foreach ($orders as $order) {
            fputcsv($handle, [...]);
        }
    });
```

### Severity: High
Export feature fails completely for large datasets.
