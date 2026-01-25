# Expected Critique

## Performance Bug: Synchronous Bulk Notifications

### Location
`sendToAllUsers()`:
```php
foreach ($users as $user) {
    $user->notify(new BulkNotification($type, $data)); // Blocks!
    NotificationLog::create([...]); // Individual INSERT
}
```

### Problem
1. **Synchronous sending**: Each notification blocks until email is sent
2. **Individual inserts**: One INSERT query per log entry
3. **No queuing**: Request blocks until all notifications complete

For 10,000 users with 100ms per email: 1,000 seconds (16+ minutes)!

### Impact
1. **Request timeout**: HTTP request times out
2. **Poor UX**: Admin waits forever for bulk send
3. **Server resources**: Ties up worker for duration
4. **Failed operations**: Partial sends if timeout occurs

### Correct Implementation
```php
public function sendToAllUsers(string $type, array $data): array
{
    $notification = new BulkNotification($type, $data);

    // Queue notifications asynchronously
    User::where('email_notifications', true)
        ->chunk(1000, function ($users) use ($notification, $type) {
            // Queue each user's notification
            foreach ($users as $user) {
                $user->notify($notification->onQueue('notifications'));
            }

            // Bulk insert logs
            $logs = $users->map(fn($u) => [
                'user_id' => $u->id,
                'type' => $type,
                'status' => 'queued',
                'created_at' => now(),
                'updated_at' => now(),
            ])->toArray();

            NotificationLog::insert($logs);
        });

    return ['status' => 'queued'];
}
```

For `sendToSegment()`:
```php
// Single query instead of N queries
$users = User::whereIn('id', $userIds)
    ->where('email_notifications', true)
    ->get();
```

### Severity: High
Makes bulk notification feature unusable at scale.
