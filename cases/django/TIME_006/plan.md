# Django Year Boundary Handling System

## Overview

This system manages time-sensitive operations that span across calendar year boundaries. The application needs to correctly handle date calculations, filtering, and aggregations when operations cross from December 31st to January 1st of the following year. This is critical for financial reporting, subscription management, and any time-based business logic that operates continuously regardless of calendar year changes.

## Requirements

1. The system must correctly calculate date ranges that span across year boundaries (e.g., December 15, 2023 to January 15, 2024)

2. Database queries must accurately filter records when the date range crosses from one year to the next

3. Time-based aggregations (sum, count, average) must include all relevant records regardless of year boundary crossings

4. The system must handle leap years correctly when calculating year-spanning periods

5. Date arithmetic operations must produce accurate results when crossing year boundaries

6. The system must maintain timezone awareness when processing year boundary transitions

7. All date comparisons must work correctly across year changes, including edge cases at midnight on December 31st/January 1st

8. The system must support both inclusive and exclusive date range queries across year boundaries

## Constraints

- All dates must be stored and processed in UTC to avoid timezone-related year boundary issues
- The system must handle the transition from December 31st 23:59:59 to January 1st 00:00:00 without data loss or incorrect calculations
- Year boundary calculations must account for different calendar systems if internationalization is required
- Performance must remain acceptable when querying large datasets across multiple years
- The system must validate that end dates in year-spanning ranges are actually after start dates

## References

See context.md for existing Django model implementations and related time handling patterns in the codebase.