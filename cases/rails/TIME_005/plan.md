# Month End Processing System

## Overview

The system needs to handle month-end date processing for financial and business operations. This includes calculating month-end dates, handling leap years, and managing date transitions across different months with varying numbers of days. The functionality is critical for financial reporting, billing cycles, and scheduled operations that depend on accurate month-end calculations.

## Requirements

1. Calculate the last day of any given month and year
2. Handle leap year calculations correctly for February (29 days in leap years, 28 in non-leap years)
3. Process month-end dates for months with 30 days (April, June, September, November)
4. Process month-end dates for months with 31 days (January, March, May, July, August, October, December)
5. Accept input parameters for month (1-12) and year (4-digit integer)
6. Return the correct day number representing the last day of the specified month
7. Handle year transitions when processing December month-end dates
8. Validate input parameters to ensure month is within valid range (1-12)
9. Validate input parameters to ensure year is a positive integer
10. Support historical dates (past years) and future dates (future years)

## Constraints

1. Month parameter must be between 1 and 12 inclusive
2. Year parameter must be a positive integer greater than 0
3. Leap year determination must follow standard Gregorian calendar rules:
   - Years divisible by 4 are leap years
   - Years divisible by 100 are not leap years
   - Years divisible by 400 are leap years
4. The system must handle edge cases around century years (1900, 2000, 2100, etc.)
5. Input validation must raise appropriate errors for invalid parameters
6. The system should not modify the input parameters
7. Results must be deterministic for the same input parameters

## References

See context.md for existing date handling implementations and related utility methods in the codebase.