# Existing Codebase

## Webhook Scenario

```
1. Payment succeeds
2. Gateway sends webhook (event_id: "evt_123")
3. Our server processes webhook, marks order as PAID
4. Network issue - gateway doesn't receive 200 OK
5. Gateway retries webhook (same event_id: "evt_123")
6. Without idempotency check: order processed again (duplicate email, double inventory release, etc.)
```

## Webhook Payload

```json
{
  "event_id": "evt_abc123",
  "event_type": "payment.completed",
  "created_at": "2024-01-15T10:30:00Z",
  "data": {
    "payment_id": "pay_xyz789",
    "order_id": "ord_456",
    "amount": 9999,
    "status": "succeeded"
  }
}
```

## Usage Guidelines

- Store processed event_ids to prevent duplicate processing
- Check if event was already processed before taking action
- Use database unique constraint on event_id
- Return 200 OK even for already-processed events (to stop retries)
- Idempotency is critical for financial operations
