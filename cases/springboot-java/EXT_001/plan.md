# Payment Gateway Integration

## Overview

Integrate with external payment gateway for processing customer payments. Must handle network issues, timeouts, and ensure order state consistency.

## Requirements

1. Process payments through external payment gateway
2. Handle payment success, failure, and timeout scenarios
3. Maintain consistent order state
4. Support payment status verification
5. Recover gracefully from network issues

## Constraints

1. Payment gateway has 30-second timeout
2. Orders must never be in undefined state
3. Customers should not be double-charged
4. Failed payments should not affect inventory
5. Timeouts require special handling (payment may have succeeded)

## References

See context.md for payment gateway API details.
