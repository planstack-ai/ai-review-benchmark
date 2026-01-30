# Order Processing with Payment

## Overview

Process orders atomically including inventory reservation, payment processing, and order creation. All steps should succeed or fail together.

## Requirements

1. Reserve inventory for ordered items
2. Process payment through external gateway
3. Create order record
4. Ensure atomicity - all or nothing
5. Handle failures gracefully

## Constraints

1. Payment is processed through external API (cannot rollback)
2. Database operations can be rolled back
3. External API calls are not transactional
4. Must handle partial failures

## References

See context.md for transaction boundaries.
