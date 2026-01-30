# Existing Codebase

## Problem Scenario

```
1. Order submission request sent
2. Server processes order, creates it
3. Response lost due to network issue
4. Client retries (thinks it failed)
5. Server creates DUPLICATE order!
```

## Usage Guidelines

- Always use idempotency keys for operations that create resources
- Include same key in all retry attempts
