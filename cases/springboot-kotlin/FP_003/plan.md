# Banking Transaction Service with Role-Based Authorization

## Overview

This application provides banking transaction management functionality where users can view their own account transactions, create deposits, withdrawals, and transfers. Administrators have additional privileges to manage transactions for any account. The system must implement proper role-based access control using Spring Security's @PreAuthorize annotations.

## Requirements

1. Implement a method to retrieve all transactions for a specific account, ordered by creation date descending
2. Implement paginated transaction retrieval for accounts
3. Implement deposit functionality that adds funds to an account and records the transaction
4. Implement withdrawal functionality that deducts funds from an account after validating sufficient balance
5. Implement transfer functionality between two accounts with proper transaction recording
6. Apply @PreAuthorize checks to ensure users can only access their own accounts (or any account if ADMIN)
7. Use the existing AccountService.isAccountOwnedByUser() method for ownership verification
8. Validate that transaction amounts are positive
9. Update account balances atomically within the transaction

## Constraints

1. Withdrawal and transfer must validate sufficient balance before proceeding
2. Transaction amounts must be positive (greater than zero)
3. All operations must be transactional (@Transactional)
4. Account must exist for all operations (throw exception if not found)
5. Transfer creates two transaction records (one for each account)
6. Use existing repository methods for data access
7. Authorization expression must check account ownership OR admin role

## References

See context.md for existing Account entity, Transaction entity, TransactionType enum, and repository interfaces.
