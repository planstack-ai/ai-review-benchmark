# Expected Critique

## Critical Bug: Non-Atomic Bundle Stock Reservation

### Location
`reserveBundleStock()` method

### Problem 1: Race Condition (Check-Then-Act)
The availability is checked first, then stock is reserved in a separate operation without a transaction or locking:

```php
$availability = $this->checkBundleAvailability($bundleId, $quantity);
// Time passes - other requests could consume stock here
if (!$availability['available']) {...}
// Stock reserved based on stale availability data
```

### Problem 2: Non-Atomic Component Reservation
Component stock is reserved in a loop without a transaction:

```php
foreach ($bundle->bundleComponents as $bundleComponent) {
    $component = Product::find($bundleComponent->component_id);
    $component->reserved_quantity += $componentQuantity;
    $component->save();
}
```

If the 3rd component fails (e.g., database error), the first 2 components remain reserved but the bundle reservation failed.

### Impact
1. **Overselling**: Two concurrent requests could both pass availability check, then both reserve
2. **Stuck inventory**: Partial reservations leave components reserved with no corresponding bundle
3. **Business rule violation**: "Component stock must be reserved atomically"
4. **Data inconsistency**: System state becomes unpredictable under concurrent load

### Correct Implementation
```php
public function reserveBundleStock(int $bundleId, int $quantity): array
{
    return DB::transaction(function () use ($bundleId, $quantity) {
        $bundle = Product::with('bundleComponents')->findOrFail($bundleId);

        // Lock all components first
        $componentIds = $bundle->bundleComponents->pluck('component_id');
        $components = Product::whereIn('id', $componentIds)
            ->lockForUpdate()
            ->get()
            ->keyBy('id');

        // Check availability with locked data
        foreach ($bundle->bundleComponents as $bundleComponent) {
            $component = $components[$bundleComponent->component_id];
            $needed = $bundleComponent->quantity * $quantity;

            if ($component->availableStock() < $needed) {
                return ['success' => false, 'message' => 'Insufficient stock'];
            }
        }

        // Reserve all atomically
        foreach ($bundle->bundleComponents as $bundleComponent) {
            $componentQuantity = $bundleComponent->quantity * $quantity;
            Product::where('id', $bundleComponent->component_id)
                ->increment('reserved_quantity', $componentQuantity);
        }

        return ['success' => true, 'reserved_quantity' => $quantity];
    });
}
```

### Severity: Critical
Can cause overselling of bundles and inventory data corruption under concurrent load.
