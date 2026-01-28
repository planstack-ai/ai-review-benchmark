# User Timezone Display System

## Overview

The application needs to display event times and timestamps to users in their local timezone. Users from different geographical locations should see times converted to their respective timezones rather than server time or UTC. This ensures a consistent user experience regardless of where users are located globally.

## Requirements

1. All datetime displays in the user interface must show times in the user's configured timezone
2. The system must detect and store each user's timezone preference
3. Event creation times must be converted from the user's timezone to UTC for storage
4. Event display times must be converted from UTC storage to the user's timezone for presentation
5. The timezone conversion must handle daylight saving time transitions correctly
6. Users must be able to update their timezone preference through their profile settings
7. The system must provide a default timezone (UTC) for users who haven't set a preference
8. All timestamp comparisons and calculations must be performed in UTC to ensure accuracy
9. The timezone display must include timezone abbreviation or offset information for clarity
10. Historical events must display in the timezone that was active at the time of the event

## Constraints

1. Timezone preferences must be validated against standard timezone identifiers
2. The system must handle edge cases where timezone data is unavailable or corrupted
3. Performance must not be significantly impacted by timezone conversions
4. The application must work correctly across different server deployment timezones
5. Timezone changes must not affect the accuracy of stored timestamp data

## References

See context.md for existing timezone handling implementations and current system architecture.