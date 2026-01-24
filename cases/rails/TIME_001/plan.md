# User Timezone Display System

## Overview

The application needs to display timestamps and time-sensitive information to users in their local timezone. Users from different geographical locations should see times converted to their preferred timezone setting, ensuring a consistent and localized user experience. This feature is critical for scheduling, notifications, and any time-based functionality where users need to understand when events occur relative to their local time.

## Requirements

1. All timestamps displayed to users must be converted to their configured timezone
2. Users must be able to set and update their preferred timezone through their profile settings
3. The system must store the user's timezone preference persistently
4. When no timezone is configured for a user, the system must use a sensible default timezone
5. Time displays must include timezone information (abbreviation or offset) for clarity
6. The system must handle timezone conversions for both past and future dates correctly
7. All user-facing time displays must respect the user's timezone setting, including:
   - Created/updated timestamps on records
   - Scheduled event times
   - Notification timestamps
   - Any other time-based information shown to users

## Constraints

1. Timezone data must be validated against standard timezone identifiers (e.g., IANA timezone database)
2. The system must handle daylight saving time transitions correctly
3. Invalid timezone settings must be rejected with appropriate error messages
4. Timezone conversion must not affect the underlying stored UTC timestamps
5. The system must gracefully handle edge cases such as times during DST transitions

## References

See context.md for existing user model structure and current timestamp handling implementations.