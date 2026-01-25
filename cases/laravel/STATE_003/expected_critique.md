# Expected Critique

## Critical Bug: Duplicate Refund Possible

### Location
`refundPayment()` method:
```php
if (!in_array($payment->status, ['completed', 'refunding'])) {
    return [
        'success' => false,
        'message' => 'Only completed payments can be refunded',
    ];
}
```

### Problem
The check allows payments in both `completed` AND `refunding` states to proceed with a refund. If a payment is already being refunded (`refunding` state), another refund call can initiate a second refund to the payment gateway.

### Impact
1. **Double refund**: Customer receives refund twice
2. **Financial loss**: Company pays out 2x the order amount
3. **Race condition**: Two concurrent refund calls both pass the check
4. **Gateway issues**: Multiple refund requests for same transaction

### Scenario
1. Payment is `completed`
2. Request A calls refund, sets status to `refunding`
3. Request B calls refund, status is `refunding` - still passes check!
4. Both requests call gateway refund
5. Customer gets refunded twice

### Secondary Issue
On refund failure, the code reverts status to `completed`:
```php
$payment->update(['status' => 'completed', ...]);
```
This loses the fact that a refund was attempted and allows immediate retry without visibility.

### Correct Implementation
```php
if ($payment->status !== 'completed') {
    return [
        'success' => false,
        'message' => 'Only completed payments can be refunded',
    ];
}
```

Or add a `refund_failed` state for failed refunds.

### Severity: Critical
Can cause direct financial loss through duplicate refunds.
