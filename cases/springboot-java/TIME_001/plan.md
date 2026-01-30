# Campaign Activity Status Check with Japan Timezone

## Overview

The system needs to determine whether marketing campaigns are currently active based on Japan Standard Time (JST). This functionality is critical for displaying appropriate campaign content to users and ensuring campaigns are only shown during their designated time periods. The system must accurately handle timezone conversions to ensure campaigns activate and deactivate at the correct local times in Japan.

## Requirements

1. The system shall check if a campaign is currently active by comparing the current Japan time against the campaign's start and end times
2. Campaign start and end times shall be stored as LocalDateTime objects representing Japan local time
3. The system shall use Japan Standard Time (JST) timezone (Asia/Tokyo) for all time comparisons
4. A campaign shall be considered active if the current Japan time is greater than or equal to the start time AND less than the end time
5. The system shall return a boolean value indicating the campaign's active status
6. The timezone conversion shall handle daylight saving time transitions correctly (though Japan does not observe DST)
7. The system shall work correctly regardless of the server's default timezone setting

## Constraints

1. Campaign end time must be after the start time
2. Both start and end times are required fields and cannot be null
3. The system must handle edge cases where current time exactly matches start or end times
4. Time comparisons must be performed in the same timezone to ensure accuracy

## References

See context.md for existing campaign management implementations and timezone handling patterns used in the codebase.