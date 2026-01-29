# Existing Codebase

## Webhook Scenario

```
1. Payment succeeds
2. Gateway sends webhook (event_id: "evt_123")
3. Our server processes webhook, marks order as PAID
4. Network issue - gateway doesn't receive 200 OK
5. Gateway retries webhook (same event_id: "evt_123")
6. Without idempotency check: order processed again!
```

## Usage Guidelines

- Store processed event_ids to prevent duplicate processing
- Return 200 OK even for already-processed events
