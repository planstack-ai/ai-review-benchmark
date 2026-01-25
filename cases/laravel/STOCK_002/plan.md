# Stock Update Service

## Overview

Service to update product stock levels when orders are placed. Must handle concurrent updates safely.

## Requirements

1. Validate product exists
2. Check sufficient stock available
3. Update stock atomically
4. Log stock changes
5. **Use atomic database operations to prevent race conditions**

## Constraints

1. Stock cannot go negative
2. Concurrent updates must be handled safely
3. Must use database-level atomicity

## References

See context.md for atomic update patterns.
