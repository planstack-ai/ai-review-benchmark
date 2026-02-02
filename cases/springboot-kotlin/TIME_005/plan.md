# Monthly Recurring Subscription Billing

## Overview

The subscription management system processes monthly recurring payments for subscribers. The system must calculate the next billing date by adding one month to the current billing date, handling edge cases where the subscription date may fall on the last days of months with varying lengths (e.g., January 31, February 28/29, etc.).

## Requirements

1. Implement a method to calculate the next billing date for recurring monthly subscriptions
2. When the current billing date is the last day of a month, the next billing should occur on the last day of the following month
3. Handle months with different lengths (28, 29, 30, or 31 days) correctly
4. When a billing date like January 31 is advanced by one month, it should correctly map to the last valid day of February (28 or 29)
5. Similarly, dates like January 30 should map to the last day of February when February doesn't have 30 days
6. The system must prevent invalid date construction errors
7. Preserve the day-of-month preference when moving to months that support that day number

## Constraints

1. Billing dates are stored as LocalDate
2. The method must handle all calendar edge cases without throwing exceptions
3. Leap years must be considered for February calculations
4. The implementation must work consistently across all months of the year
5. Invalid dates (like February 30 or February 31) must never be constructed
6. The calculation should maintain the subscriber's preferred billing day when possible

## References

See context.md for existing subscription entity structure and billing implementations.
