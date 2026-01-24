# External API Call Transaction Management

## Overview

The system needs to integrate with external payment processing services to handle customer transactions. When processing orders, the application must communicate with third-party APIs to validate payment methods, process charges, and update transaction records. This integration requires careful management of database transactions to ensure data consistency while avoiding potential issues with external service calls.

## Requirements

1. All external API calls must be executed outside of active database transactions
2. Database operations that depend on external API responses must be performed after the API call completes successfully
3. Transaction rollback mechanisms must not affect external API calls that have already been executed
4. External API failures must not leave database transactions in an incomplete state
5. Payment processing workflow must maintain data integrity between local database and external service states
6. Error handling must properly manage both database transaction failures and external API failures
7. The system must prevent database connection timeouts caused by long-running external API calls within transactions
8. Retry logic for failed external API calls must not interfere with database transaction management

## Constraints

1. External API calls may take up to 30 seconds to complete
2. Database transaction timeout is configured to 10 seconds
3. Payment API responses must be validated before committing any database changes
4. Failed transactions must not result in duplicate charges to external payment systems
5. The system must handle network timeouts and service unavailability gracefully
6. All payment-related operations must be logged for audit purposes

## References

See context.md for existing transaction management patterns and database configuration details.