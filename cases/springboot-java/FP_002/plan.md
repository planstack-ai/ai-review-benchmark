# Banking Service

## Overview

This service provides comprehensive banking operations including fund transfers between accounts, deposits, withdrawals, and transaction history inquiry. The system ensures data consistency through pessimistic locking and proper transactional boundaries.

## Requirements

1. Implement fund transfer between two accounts with pessimistic locking
2. Implement deposit functionality that credits an account and records the transaction
3. Implement withdrawal functionality that debits an account and records the transaction
4. Implement transaction history retrieval for an account (ordered by creation date descending)
5. Implement account balance inquiry
6. Validate that all transaction amounts are positive (greater than zero)
7. Create and persist a Transaction record for each operation with appropriate TransactionType
8. Use constructor injection for dependencies

## Constraints

1. All write operations must be transactional (@Transactional)
2. Transaction history and balance inquiry must be read-only transactional
3. Account must exist for all operations (throw AccountNotFoundException if not found)
4. Use findByAccountNumberWithLock for write operations to prevent concurrent modification
5. Transfer operation sets fromAccount and toAccount on the Transaction
6. Deposit operation sets toAccount only (fromAccount is null)
7. Withdrawal operation sets fromAccount only (toAccount is null)
8. Insufficient balance is handled by Account.debit() method (throws InsufficientFundsException)

## References

See context.md for Account entity with credit/debit methods, Transaction entity, TransactionType enum, and repository interfaces with locking queries.
