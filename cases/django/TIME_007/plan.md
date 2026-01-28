# Business Day Delivery Calculator

## Overview

This system calculates delivery dates for orders by adding business days to the order date. Business days exclude weekends (Saturday and Sunday) and should provide accurate delivery estimates for customer orders. The system needs to handle various scenarios including orders placed on weekends, holidays, and edge cases around month/year boundaries.

## Requirements

1. Calculate delivery date by adding a specified number of business days to a given start date
2. Business days must exclude Saturdays and Sundays from the calculation
3. Accept start date as a date object and business days as a positive integer
4. Return the calculated delivery date as a date object
5. Handle cases where the start date falls on a weekend by treating it as a valid starting point
6. Support calculation across month and year boundaries
7. Validate that the number of business days is a positive integer
8. Raise appropriate exceptions for invalid input parameters
9. Handle leap years correctly when calculations span February
10. Ensure the function works for both small (1-5 days) and large (50+ days) business day calculations

## Constraints

1. Business days parameter must be greater than zero
2. Start date must be a valid date object
3. The calculation should not consider holidays beyond weekends
4. Maximum supported business days calculation should be reasonable (e.g., up to 365 business days)
5. Function should handle edge cases like December 31st to January dates
6. Input validation should raise ValueError for invalid parameters
7. The function should be deterministic - same inputs always produce same outputs

## References

See context.md for existing date utility implementations and Django model patterns that may be relevant to this business day calculation feature.