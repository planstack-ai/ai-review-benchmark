# Expected Critique

## Critical Bug: Subscription Activation Without State Check

### Location
`activate()` method:
```php
public function activate(int $subscriptionId): array
{
    $subscription = Subscription::findOrFail($subscriptionId);

    // BUG: No state check - allows activation from any state
    $subscription->update([
        'status' => 'active',
        'current_period_ends_at' => now()->addMonth(),
    ]);
```

### Problem
The `activate()` method doesn't check the current subscription state before transitioning to active. According to the valid transitions:
- `trial → active` (allowed)
- `paused → active` (allowed via resume)
- `cancelled → active` (NOT allowed)
- `expired → active` (NOT allowed)

### Impact
1. **Revenue loss**: Cancelled users can reactivate without payment
2. **Business rule violation**: Expired subscriptions should require new signup
3. **Audit issues**: State history becomes meaningless
4. **Billing confusion**: Reactivated subscriptions may not have proper billing setup

### Secondary Bug
The `cancel()` method also lacks proper state validation - it allows cancelling already cancelled or expired subscriptions.

### Correct Implementation
```php
public function activate(int $subscriptionId): array
{
    $subscription = Subscription::findOrFail($subscriptionId);

    if (!in_array($subscription->status, ['trial', 'paused'])) {
        return [
            'success' => false,
            'message' => 'Only trial or paused subscriptions can be activated',
        ];
    }

    $subscription->update([
        'status' => 'active',
        'current_period_ends_at' => now()->addMonth(),
    ]);

    return ['success' => true, 'subscription' => $subscription];
}
```

### Severity: High
Allows bypassing the subscription lifecycle and reactivating cancelled subscriptions.
