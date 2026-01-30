# Existing Codebase

## Concurrent Update Scenario

```
Thread A: reads inventory (quantity = 100)
Thread B: reads inventory (quantity = 100)
Thread A: decrements by 5, saves (quantity = 95)
Thread B: decrements by 3, saves (quantity = 97)  -- Thread A's update is lost!
```

## Usage Guidelines

- Use @Version for optimistic locking on entities with concurrent updates
- Handle OptimisticLockException with retry logic
