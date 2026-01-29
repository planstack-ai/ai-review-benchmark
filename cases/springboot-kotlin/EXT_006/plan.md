# Shipping Label Generation

## Overview

Generate shipping labels through external carrier API. Label generation is critical for order fulfillment.

## Requirements

1. Generate shipping labels via carrier API
2. Store tracking numbers in order
3. Handle API failures appropriately
4. Notify operations team of failures
5. Support multiple carriers

## Constraints

1. Carrier API may be unavailable
2. Failed label generation should not block order processing
3. Operations team must be notified of failures
4. Retry should be possible for failed labels

## References

See context.md for carrier integration details.
