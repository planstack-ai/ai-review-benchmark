# Bulk User Metrics Update

## Overview

The system needs to periodically update user engagement metrics based on their activity. This runs as a scheduled job processing all active users.

## Requirements

1. Update last_active timestamp for users with recent activity
2. Calculate and update user engagement scores
3. Process all active users (potentially 100k+)
4. Run as nightly batch job
5. Track processing statistics

## Constraints

1. Job must complete within 2 hours
2. Must not lock tables for extended periods
3. Should handle partial failures gracefully
4. Memory usage must be bounded

## References

See context.md for existing service methods.
