# Campaign Activity Status Check with Japan Timezone

## Overview

The system needs to determine whether marketing campaigns are currently active based on their configured start and end times. Campaign activity status is critical for displaying relevant promotions to users and ensuring campaigns run only during their intended timeframes. All campaign scheduling must be evaluated against Japan Standard Time (JST) to maintain consistency across the platform.

## Requirements

1. The system must provide a method to check if a campaign is currently active
2. Campaign activity must be determined by comparing the current time against the campaign's start and end times
3. All time comparisons must be performed using Japan Standard Time (JST/Asia/Tokyo timezone)
4. A campaign is considered active if the current JST time falls between the campaign's start time (inclusive) and end time (exclusive)
5. The system must handle campaigns that span multiple days correctly
6. The method must return a boolean value indicating the campaign's active status
7. The implementation must account for timezone differences when the server is running in a different timezone than JST

## Constraints

1. Campaign start time must be before or equal to the end time
2. Both start and end times are required fields and cannot be null
3. The system must handle daylight saving time transitions correctly for JST
4. Performance should be optimized for frequent status checks
5. The implementation must be thread-safe for concurrent access

## References

See context.md for existing campaign entity structure and related implementations.