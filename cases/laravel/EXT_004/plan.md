# Retry Duplicate Order Handling System

## Overview

When customers experience network issues or click submit buttons multiple times, duplicate order creation requests can occur. The system must handle these retry scenarios gracefully by detecting duplicate orders and returning the original order instead of creating a new one. This prevents customers from being charged multiple times and ensures data consistency in the order management system.

## Requirements

1. Detect duplicate order creation attempts based on a unique identifier provided by the client
2. Return the existing order when a duplicate creation request is detected
3. Ensure the duplicate detection mechanism works across concurrent requests
4. Maintain transactional integrity during order creation and duplicate checking
5. Log duplicate order attempts for monitoring and debugging purposes
6. Return appropriate HTTP status codes for both new orders and duplicate detections
7. Include the same order data structure in responses for both new and existing orders
8. Handle race conditions where multiple identical requests arrive simultaneously
9. Validate that the duplicate order belongs to the same customer making the request
10. Ensure the duplicate detection does not interfere with legitimate separate orders

## Constraints

1. The unique identifier for duplicate detection must be provided by the client
2. Duplicate detection should only apply within a reasonable time window
3. The system must not create partial orders when duplicate detection fails
4. Database constraints should prevent duplicate orders at the data layer
5. The duplicate order response must not expose sensitive information from other customers' orders
6. Performance impact of duplicate checking should be minimal for normal order flow

## References

See context.md for existing order creation patterns and database schema details.