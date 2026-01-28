# Campaign Period Check Implementation Plan

## Overview

This feature implements a campaign discount system that validates whether a campaign is currently active based on its configured time period. The system must ensure that discounts are only applied when the current time falls within the campaign's valid start and end dates, providing accurate promotional pricing for customers.

## Requirements

1. Create a campaign entity that stores start date, end date, and discount percentage
2. Implement a service method that checks if a campaign is currently active
3. The active check must compare the current system time against the campaign's start and end dates
4. Apply the campaign discount only when the campaign is determined to be active
5. Return the original price when no active campaign exists
6. Support campaigns with different discount percentages
7. Handle timezone considerations appropriately for date comparisons
8. Provide a method to calculate the final price after applying valid campaign discounts

## Constraints

1. Campaign start date must be before or equal to the end date
2. Discount percentage must be between 0 and 100
3. The system must handle null or missing campaign data gracefully
4. Time comparisons must be precise to avoid edge case errors at campaign boundaries
5. The service must not apply expired campaigns even if they exist in the system
6. Future campaigns (not yet started) should not be applied

## References

See context.md for existing date/time handling patterns and service layer implementations used in the codebase.