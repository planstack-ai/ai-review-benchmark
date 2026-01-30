# Order Submission with Retry

## Overview

Submit orders to fulfillment system with automatic retry on failure. Network issues should not cause failed orders.

## Requirements

1. Submit order to external fulfillment API
2. Retry on network failures
3. Prevent duplicate order submissions
4. Handle partial failures gracefully
5. Maintain order consistency

## Constraints

1. Network can fail at any time
2. Retries should not create duplicate orders
3. External system may or may not support idempotency
4. Must handle both client and server errors differently

## References

See context.md for retry configuration.
