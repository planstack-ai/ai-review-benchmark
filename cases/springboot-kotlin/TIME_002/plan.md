# Campaign Date Boundary Validation System

## Overview

The system manages marketing campaigns with specific validity periods. Each campaign has a start date and an end date that defines when the campaign is active and available to users. The business requirement is that campaigns remain valid through the entire end date specified, meaning a campaign ending on December 31st should be accessible throughout that entire day until midnight.

## Requirements

1. Campaign entities must have clearly defined start and end date fields
2. The system must validate that a campaign's end date is not before its start date
3. Campaign validity checking must determine if the current date/time falls within the campaign period
4. A campaign must remain valid through the complete end date specified (until 23:59:59 of that date)
5. The system must provide a method to check if a campaign is currently active
6. Date comparisons must account for the full day boundary of the end date
7. The validation logic must handle edge cases around midnight transitions
8. Campaign status queries must return accurate results for dates exactly matching the end date

## Constraints

- End dates must be inclusive of the entire specified day
- Start dates begin at 00:00:00 of the specified date
- End dates conclude at 23:59:59 of the specified date
- The system must handle timezone considerations appropriately
- Date validation must prevent logical inconsistencies (end before start)
- Current time comparisons must be precise to avoid premature campaign expiration

## References

See context.md for existing campaign management patterns and date handling implementations in the codebase.