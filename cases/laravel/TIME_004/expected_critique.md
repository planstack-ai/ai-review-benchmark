# Expected Critique

## Critical Bug: Month-End Billing Date Overflow

### Location
`calculateNextBillingDate()` method:
```php
$nextBilling = $currentPeriodEnd->copy()->addMonth();
$nextBilling->day = $billingDay;
```

### Problem
When setting the day directly without checking if it exists in the month, Carbon will overflow to the next month.

### Example
- Customer billing_day: 31
- Current period ends: January 31, 2024
- Code adds month: February 2024
- Sets day to 31: **March 2 or 3, 2024** (overflow!)
- Expected: February 29, 2024 (last day of Feb in leap year)

### Impact
1. **Billing gap**: Customer billed in March instead of February
2. **Revenue delay**: One month billing cycle becomes ~2 months
3. **Inconsistent billing**: Dates drift over time
4. **Customer confusion**: Unpredictable billing dates

### Note
The code even has `getMonthlyBillingDate()` that handles this correctly, but `calculateNextBillingDate()` doesn't use it!

### Correct Implementation
```php
public function calculateNextBillingDate(Subscription $subscription): Carbon
{
    $currentPeriodEnd = Carbon::parse($subscription->current_period_end);
    $billingDay = $subscription->billing_day;

    $nextBilling = $currentPeriodEnd->copy()->addMonth()->startOfMonth();
    $lastDayOfMonth = $nextBilling->daysInMonth;

    $nextBilling->day = min($billingDay, $lastDayOfMonth);

    return $nextBilling;
}
```

Or use the existing helper:
```php
public function calculateNextBillingDate(Subscription $subscription): Carbon
{
    $nextMonth = Carbon::parse($subscription->current_period_end)->addMonth();
    return $this->getMonthlyBillingDate($subscription->billing_day, $nextMonth);
}
```

### Severity: High
Causes incorrect billing dates for any customer with billing day 29-31.
