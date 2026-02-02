# FP_010: Intentional Modifying Query

## Overview

Implement a bulk update operation using `@Modifying` annotation without entity listeners. This is a **CORRECT** implementation that may appear suspicious to reviewers who expect entity lifecycle events to be triggered.

## Requirements

- Bulk update user last login timestamps for performance
- Use native SQL query with `@Modifying` annotation
- Skip entity listener callbacks intentionally for performance
- Document why entity manager clearing is not needed

## Why This Looks Suspicious But Is Correct

### What Looks Wrong

1. `@Modifying` query without `clearAutomatically = true`
2. No entity listener callbacks triggered
3. Direct SQL update bypassing JPA lifecycle
4. Potential for stale data in persistence context

### Why It's Actually Correct

1. **Performance optimization**: Bulk updates are faster than loading entities
2. **No business logic needed**: Simple timestamp update doesn't require entity validation
3. **Isolated operation**: This method is called in contexts where no entity caching occurs
4. **Read-through pattern**: Subsequent reads will fetch fresh data from database
5. **Intentional design**: Entity listeners would add unnecessary overhead for this operation

### When This Pattern Is Appropriate

- Simple field updates without business logic
- High-volume batch operations
- When entity cache is not populated
- When subsequent operations don't rely on cached state
- Performance-critical paths where entity overhead is unnecessary
