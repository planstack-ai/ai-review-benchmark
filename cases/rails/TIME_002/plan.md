# Sale Period Boundary Management

## Overview

The system needs to manage sale periods with precise timing boundaries to ensure sales are active only during their designated timeframes. This functionality is critical for e-commerce platforms where promotional pricing must start and end at exact times to maintain customer trust and business integrity. The sale period boundary logic determines when discounted prices become available to customers.

## Requirements

1. Sales must become active at exactly midnight (00:00:00) on the specified start date
2. The system must use the application's configured timezone for all sale period calculations
3. Sale status checks must return true only when the current time is within the active sale period
4. The start date must be treated as inclusive (sale is active from the beginning of that day)
5. The end date must be treated as inclusive (sale remains active through the end of that day)
6. Sale period validation must occur in real-time when checking sale status
7. The system must handle timezone conversions correctly when comparing dates and times

## Constraints

1. Start date cannot be in the past when creating a new sale
2. End date must be after the start date
3. Sale periods cannot overlap for the same product
4. The system must handle daylight saving time transitions correctly
5. Sale status must be deterministic - the same input parameters should always produce the same result
6. Performance considerations: sale status checks may be called frequently and should be optimized

## References

See context.md for existing sale management implementations and related timezone handling patterns in the codebase.