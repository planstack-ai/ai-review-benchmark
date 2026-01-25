# Expected Critique

## Critical Bug: Timezone Not Converted to UTC

### Location
`createSale()` method:
```php
$start = Carbon::parse($startsAt, $timezone);
$end = Carbon::parse($endsAt, $timezone);
// ...
'starts_at' => $start,
'ends_at' => $end,
```

### Problem
The code parses the times with the given timezone, but doesn't convert them to UTC before storing. When Laravel saves the Carbon instance to the database, it uses the time value as-is without timezone conversion.

### Example
- Admin creates sale: "10:00 AM Tokyo time" (Asia/Tokyo, UTC+9)
- Code: `Carbon::parse('10:00', 'Asia/Tokyo')` creates 10:00 with Asia/Tokyo timezone
- Database stores: `10:00:00` (as if it were UTC)
- Comparison with `now()` (UTC): Sale active at 10:00 UTC, not 10:00 Tokyo time
- Actual intended time: 01:00 UTC (10:00 Tokyo = 01:00 UTC)
- **Sale starts 9 hours late!**

### Impact
1. **Sale timing off**: Sales start/end at wrong times
2. **Customer confusion**: Sale not active when advertised
3. **Revenue loss**: Customers miss sale windows
4. **International issues**: Different errors for different timezones

### Correct Implementation
```php
public function createSale(string $name, string $startsAt, string $endsAt, string $timezone): array
{
    // Parse in given timezone, then convert to UTC for storage
    $start = Carbon::parse($startsAt, $timezone)->utc();
    $end = Carbon::parse($endsAt, $timezone)->utc();

    // Now the comparison with now() (UTC) will be correct
    // ...
}
```

Or use `->setTimezone('UTC')`:
```php
$start = Carbon::parse($startsAt, $timezone)->setTimezone('UTC');
```

### Severity: High
Flash sales will be active at wrong times, causing customer complaints and lost revenue.
