# Month End Processing System

## Overview

The system needs to handle month-end financial processing operations that occur on the last business day of each month. This includes calculating month-end balances, generating reports, and scheduling follow-up tasks. The system must correctly identify month-end dates across different months, including those with varying numbers of days (28, 29, 30, 31) and handle leap years appropriately.

## Requirements

1. The system shall identify the last day of any given month accurately
2. The system shall handle leap years correctly when processing February dates
3. The system shall calculate month-end dates for months with 30 days (April, June, September, November)
4. The system shall calculate month-end dates for months with 31 days (January, March, May, July, August, October, December)
5. The system shall process month-end operations only on valid calendar dates
6. The system shall accept month and year parameters as input for month-end calculations
7. The system shall return the correct last day of the month as a date object
8. The system shall validate that the provided month is between 1 and 12
9. The system shall validate that the provided year is a positive integer
10. The system shall handle edge cases where the current date might affect month-end processing logic

## Constraints

- Month values must be integers between 1 and 12 (inclusive)
- Year values must be positive integers
- The system must not assume all months have the same number of days
- February must be handled differently in leap years versus non-leap years
- Invalid date combinations should raise appropriate exceptions
- The system should not hardcode month lengths but calculate them dynamically

## References

See context.md for existing date utility functions and Django model implementations that may be relevant to this month-end processing system.