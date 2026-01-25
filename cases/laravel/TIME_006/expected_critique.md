# Expected Critique

## Bug: DST Causes Recurring Event Time Drift

### Location
`generateOccurrences()` method:
```php
$currentStart->addDays(7);
```

### Problem
The code adds exactly 7 days (168 hours) to the UTC timestamp. During daylight saving time transitions, this causes the wall clock time to shift by 1 hour.

### Example (US Eastern Time)
- Event: Every Monday at 10:00 AM Eastern
- March 4, 2024: 10:00 AM EST = 15:00 UTC, stored correctly
- March 11, 2024: DST begins, clocks spring forward
- Code adds 168 hours to 15:00 UTC → 15:00 UTC
- **But** 15:00 UTC on March 11 = 11:00 AM EDT (not 10:00 AM!)

The event now occurs at 11:00 AM wall clock time instead of 10:00 AM.

### Business Rule Violation
> DST transitions should maintain wall clock time

Users expect "10:00 AM every Monday" to always be at 10:00 AM on their clock.

### Impact
1. **Missed meetings**: Users show up at wrong time
2. **Confusion**: Event appears at different time after DST
3. **Accumulation**: Error persists for all future occurrences

### Correct Implementation
```php
public function generateOccurrences(Event $event): void
{
    $timezone = $event->timezone;
    $start = Carbon::parse($event->start_time)->setTimezone($timezone);
    $end = Carbon::parse($event->end_time)->setTimezone($timezone);
    $duration = $start->diffInMinutes($end);

    // Store wall clock time components
    $hour = $start->hour;
    $minute = $start->minute;
    $dayOfWeek = $start->dayOfWeek;

    $current = $start->copy();
    $recurrenceEnd = $event->recurrence_end
        ? Carbon::parse($event->recurrence_end, $timezone)
        : now()->addMonths(3);

    while ($current->lte($recurrenceEnd)) {
        EventOccurrence::create([
            'event_id' => $event->id,
            'start_time' => $current->copy()->utc(),
            'end_time' => $current->copy()->addMinutes($duration)->utc(),
        ]);

        // Add 1 week in local timezone (maintains wall clock time)
        $current->addWeek();
    }
}
```

### Severity: Medium
Affects recurring events during DST transition periods (~2x per year).
