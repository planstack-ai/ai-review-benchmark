# Expected Critique

## Bug: Reminder Timezone Ignored

### Location
`sendReminder()` method:
```php
// Sends immediately instead of scheduling for 9 AM user timezone
$user->notify($notification);
```

### Problem
The requirements specify:
> Send at 9 AM in user's timezone

But the code sends notifications immediately when the job runs, ignoring the user's timezone preference.

### Impact
1. **Poor user experience**: Reminders arrive at random times
2. **Users in different timezones**: May receive emails at 3 AM
3. **Lower engagement**: Off-hours emails often ignored
4. **Requirement violation**: Explicitly ignores scheduling requirement

### Correct Implementation
```php
private function sendReminder(Subscription $subscription, string $type): void
{
    $user = $subscription->user;

    if ($subscription->status === 'cancelled') {
        return;
    }

    $notification = $type === '7d'
        ? new SubscriptionExpiringNotification($subscription)
        : new SubscriptionFinalReminderNotification($subscription);

    // Calculate 9 AM in user's timezone
    $userNow = now()->setTimezone($user->timezone);
    $sendAt = $userNow->copy()->setTime(9, 0, 0);

    // If 9 AM already passed today, schedule for tomorrow
    if ($sendAt->isPast()) {
        $sendAt->addDay();
    }

    // Convert back to UTC for queue
    $sendAt->setTimezone('UTC');

    // Schedule the notification
    $user->notify($notification->delay($sendAt));

    $subscription->update([
        "reminder_{$type}_sent" => true,
    ]);
}
```

Or use Laravel's notification scheduling:
```php
$user->notify(
    $notification->delay(
        Carbon::parse('09:00:00', $user->timezone)->utc()
    )
);
```

### Secondary Issues
1. Query uses `whereDate()` which ignores time portion, potentially catching subscriptions at wrong times
2. Marks as sent before confirming notification delivery

### Severity: Medium
Violates explicit scheduling requirement, degrading user experience.
