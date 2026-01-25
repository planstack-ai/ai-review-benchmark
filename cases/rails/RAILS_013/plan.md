# Account Balance Transfer Service

## Overview

Implement a service to transfer funds between two accounts. The service must handle concurrent transfer requests safely and ensure that account balances remain consistent. Transfers should be atomic - either both accounts are updated or neither is.

## Requirements

1. Transfer specified amount from source account to destination account
2. Validate that source account has sufficient balance before transfer
3. Raise InsufficientFunds error if source balance is less than transfer amount
4. Deduct amount from source account balance
5. Add amount to destination account balance
6. Ensure atomicity - both balance updates must succeed or both must fail
7. Handle concurrent transfer requests correctly

## Constraints

1. Account balances must never go negative
2. Transfer operations must be thread-safe and handle concurrent requests
3. Total money in the system must be conserved (no money created or destroyed)
4. Use database transactions for atomicity

## References

See context.md for Account model and error class definitions.
