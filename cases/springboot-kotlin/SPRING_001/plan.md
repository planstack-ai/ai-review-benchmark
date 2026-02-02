# Order Processing with Transactional Atomicity

## Overview

This system handles order processing that includes both order creation and payment processing. The business requirement is that these two operations must be executed atomically - either both succeed or both fail together. This ensures data consistency and prevents scenarios where an order exists without a corresponding payment or vice versa.

## Requirements

1. Create an OrderService that handles order creation and payment processing in a single transaction
2. Implement a PaymentService that processes payments for orders
3. The order creation and payment processing must be executed atomically within the same transaction
4. If payment processing fails, the order creation must be rolled back
5. If order creation fails, no payment should be processed
6. The system must use Spring's @Transactional annotation to manage transaction boundaries
7. Services must be properly configured to participate in the same transaction scope
8. The application must demonstrate proper transaction propagation behavior
9. Include appropriate error handling that preserves transactional integrity
10. Provide a REST endpoint that triggers the order processing workflow

## Constraints

1. Payment amounts must be positive values
2. Orders must have valid customer information
3. The system must handle payment service failures gracefully
4. Database operations must be properly rolled back on any failure in the transaction chain
5. No partial data should persist if any step in the process fails

## References

See context.md for existing service implementations and database configuration patterns.