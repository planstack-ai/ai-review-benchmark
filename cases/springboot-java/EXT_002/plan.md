# Payment Webhook Handler

## Overview

Handle webhook callbacks from payment gateway for payment status updates. Webhooks may be delivered multiple times due to retries.

## Requirements

1. Receive payment status updates via webhook
2. Update order status based on payment result
3. Handle webhook retries from payment provider
4. Ensure each payment event is processed only once
5. Return appropriate HTTP status codes

## Constraints

1. Webhooks may be delivered multiple times
2. Processing same webhook twice must not cause duplicate actions
3. Must verify webhook signature for security
4. Must respond within 30 seconds to avoid retry

## References

See context.md for webhook payload format.
