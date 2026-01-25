# Expected Critique

## Bug: Alert Timestamp Updated Before Send

### Location
`sendLowStockAlert()` method:
```php
private function sendLowStockAlert(Product $product): void
{
    $managers = User::where('role', 'inventory_manager')->get();

    // Updates BEFORE sending
    $product->update(['last_low_stock_alert_at' => now()]);

    // If this fails, timestamp is already updated!
    Notification::send($managers, new LowStockAlertNotification($product));
}
```

### Problem
The timestamp is updated before the notification is actually sent. If the notification fails (email server down, exception thrown, etc.), the product is marked as "alert sent" but no one received it.

### Impact
1. **Missed alerts**: Failed notifications are never retried
2. **Stock outages**: Managers don't know about low stock
3. **Silent failures**: No indication that alert wasn't delivered
4. **24-hour gap**: Can't retry for 24 hours due to cooldown

### Correct Implementation
```php
private function sendLowStockAlert(Product $product): void
{
    $managers = User::where('role', 'inventory_manager')->get();

    // Send first
    Notification::send($managers, new LowStockAlertNotification($product));

    // Only update timestamp after successful send
    $product->update(['last_low_stock_alert_at' => now()]);
}
```

Or with try-catch:
```php
private function sendLowStockAlert(Product $product): void
{
    $managers = User::where('role', 'inventory_manager')->get();

    try {
        Notification::send($managers, new LowStockAlertNotification($product));
        $product->update(['last_low_stock_alert_at' => now()]);
    } catch (\Exception $e) {
        \Log::error("Failed to send low stock alert for product {$product->id}: {$e->getMessage()}");
        // Don't update timestamp - allow retry
    }
}
```

### Severity: Medium
Can cause important inventory alerts to be silently lost.
