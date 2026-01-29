# Existing Codebase

## Timeout Scenario

```
1. Customer submits order
2. Payment request sent to gateway
3. Network timeout after 30 seconds
4. Unknown if payment was processed!
5. Customer may have been charged
```

## Usage Guidelines

- Timeout does NOT mean payment failed - it's unknown
- Mark orders as PENDING_VERIFICATION on timeout
- Never assume payment failed on timeout
