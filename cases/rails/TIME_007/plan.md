# Business Day Delivery Calculator

## Overview

This feature calculates delivery dates for orders by adding a specified number of business days to a given start date. Business days are defined as Monday through Friday, excluding weekends (Saturday and Sunday). The system needs to handle various scenarios including orders placed on weekends, holidays, and edge cases around month and year boundaries.

## Requirements

1. Calculate delivery date by adding business days to a start date
2. Skip weekends (Saturday and Sunday) when counting business days
3. Accept start date and number of business days as input parameters
4. Return the calculated delivery date as a Date object
5. Handle cases where the start date falls on a weekend by treating it as the next business day
6. Support calculation of 1 to 30 business days from the start date
7. Properly handle month boundaries when adding business days
8. Properly handle year boundaries when adding business days
9. Validate that the number of business days is a positive integer
10. Validate that the start date is a valid Date object

## Constraints

1. Business days parameter must be between 1 and 30 (inclusive)
2. Start date cannot be nil or invalid
3. Weekend days (Saturday = 6, Sunday = 0 in Ruby's wday) are not counted as business days
4. If start date is a weekend, begin counting from the following Monday
5. The calculation should be efficient and not rely on iterating through every single day
6. Handle leap years correctly when crossing year boundaries
7. Return appropriate error messages for invalid inputs

## References

See context.md for existing date utility implementations and business day calculation patterns used elsewhere in the codebase.