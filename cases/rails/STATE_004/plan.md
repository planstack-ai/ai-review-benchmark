# Duplicate Payment Prevention System

## Overview

The system must prevent duplicate payments for the same order to protect against financial losses and maintain data integrity. This is a critical business requirement where customers should only be charged once per order, regardless of network issues, user behavior, or system failures that might cause multiple payment attempts.

## Requirements

1. Each order must accept payment exactly once during its lifecycle
2. Subsequent payment attempts for the same order must be rejected with an appropriate error message
3. The system must track payment status at the order level to determine if payment has already been processed
4. Payment rejection must occur before any financial transaction is initiated
5. The system must handle concurrent payment attempts for the same order safely
6. Payment status must be persisted immediately upon successful payment processing
7. The system must distinguish between failed payment attempts (which should allow retry) and successful payments (which should prevent further attempts)
8. Error messages for duplicate payment attempts must clearly indicate the reason for rejection

## Constraints

1. Payment status checks must be atomic to prevent race conditions
2. The system must not rely solely on external payment processor responses to determine duplicate status
3. Payment attempts on orders that have never had a payment processed should be allowed
4. The duplicate prevention mechanism must not interfere with legitimate payment retries after failures
5. System must handle edge cases where payment processing succeeds but status update fails

## References

See context.md for existing payment processing implementations and related system components.