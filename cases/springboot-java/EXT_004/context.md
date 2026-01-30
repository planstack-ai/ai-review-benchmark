# Existing Codebase

## Problem Scenario

```
1. Order submission request sent
2. Server processes order, creates it
3. Response lost due to network issue
4. Client retries (thinks it failed)
5. Server creates DUPLICATE order!
```

## Spring Retry Configuration

```java
@Configuration
@EnableRetry
public class RetryConfig {
    // Retry up to 3 times with exponential backoff
}
```

## Idempotency Pattern

```java
// Good: Include idempotency key
POST /orders
Idempotency-Key: "order_12345_attempt_1"
{...order data...}

// Server checks if this key was already processed
// If yes, return cached response instead of creating duplicate
```

## Usage Guidelines

- Always use idempotency keys for operations that create resources
- Generate idempotency key on client side before first attempt
- Include same key in all retry attempts
- Server should store and check idempotency keys
- Return cached response for duplicate keys
