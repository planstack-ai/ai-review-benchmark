# Date Only Comparison System

## Overview

The system needs to provide functionality for comparing dates while completely ignoring the time component. This is essential for business logic that operates on calendar dates rather than specific timestamps, such as determining if events occur on the same day, checking date ranges for scheduling, or filtering records by date regardless of when during that date they were created.

## Requirements

1. The system must provide a function that compares two datetime objects and returns True if they represent the same calendar date
2. The comparison must ignore hours, minutes, seconds, and microseconds completely
3. The function must handle Django's timezone-aware datetime objects correctly
4. The function must work with datetime objects from different timezones that represent the same calendar date
5. The function must accept both datetime.datetime and datetime.date objects as input
6. The function must return a boolean value indicating whether the dates match
7. The function must be named `dates_equal` and accept two parameters: `date1` and `date2`
8. The function must handle None values gracefully by returning False when either parameter is None
9. The function must raise appropriate exceptions for invalid input types

## Constraints

1. The comparison must account for timezone differences - dates that appear different in UTC but represent the same local date should be considered equal
2. The function must not modify the original datetime objects passed as parameters
3. Performance should be optimized for frequent comparisons in web request contexts
4. The function must work consistently across different Django timezone settings
5. Edge cases around daylight saving time transitions must be handled correctly

## References

See context.md for existing date handling patterns and timezone configuration in the Django application.