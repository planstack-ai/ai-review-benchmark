# Payment Processing Workflow

## Overview

Handle payment state transitions for order payments.

## Requirements

1. Create payment in pending state
2. Process through payment gateway
3. Handle success/failure appropriately
4. Support refunds for completed payments

## Valid States

- pending → processing (submitted to gateway)
- processing → completed (gateway confirms)
- processing → failed (gateway rejects)
- completed → refunding (refund initiated)
- refunding → refunded (refund confirmed)
- failed → pending (retry allowed)
