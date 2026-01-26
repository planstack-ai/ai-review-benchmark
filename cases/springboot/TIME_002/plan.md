# Campaign Date Boundary Validation System

## Overview

The system manages marketing campaigns with specific validity periods. Each campaign has a start date and an end date that defines when the campaign is active and available to customers. The business requirement is that campaigns should remain valid through the entire end date specified, meaning a campaign ending on December 31st should be accessible until the very end of that day (23:59:59).

## Requirements

1. Campaign entities must have clearly defined start and end date fields
2. The system must validate that a campaign's end date is not before its start date
3. Campaign validity checking must determine if the current date/time falls within the campaign period
4. A campaign must be considered valid from the beginning of the start date (00:00:00)
5. A campaign must remain valid until the end of the specified end date (23:59:59)
6. The system must provide a method to check if a campaign is currently active
7. Date comparisons must account for time zones appropriately
8. The validation logic must handle edge cases around midnight transitions

## Constraints

- End date cannot be null or empty
- Start date cannot be null or empty
- End date must be on or after the start date
- Date validation must be performed before saving campaign data
- System must handle leap years and month boundary transitions correctly
- Time zone handling must be consistent across all date operations

## References

See context.md for existing campaign management patterns and date handling utilities in the codebase.