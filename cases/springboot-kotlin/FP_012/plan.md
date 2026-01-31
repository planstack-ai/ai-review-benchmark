# FP_012: Optimized Counter Cache

## Overview

Implement a denormalized counter field for performance optimization. This is a **CORRECT** implementation that may appear to have data consistency risks to reviewers who expect normalized database designs.

## Requirements

- Store post comment count in denormalized field on Post entity
- Maintain counter consistency with database triggers
- Add check constraint to validate counter accuracy
- Use counter for fast queries without JOIN

## Why This Looks Suspicious But Is Correct

### What Looks Wrong

1. Denormalized `comment_count` field duplicates information
2. Could become inconsistent with actual comment count
3. Manual counter management looks error-prone
4. Violates database normalization principles
5. No obvious synchronization mechanism in code

### Why It's Actually Correct

1. **Database-enforced consistency**: Triggers automatically maintain count
2. **Check constraint validation**: Database prevents invalid states
3. **Performance optimization**: Avoids expensive COUNT() queries and JOINs
4. **Read-heavy workload**: Post listings query comment counts frequently
5. **Proven pattern**: Counter cache is a standard optimization technique

### Counter Cache Pattern Components

**Database Layer:**
- Trigger on INSERT: Increments counter
- Trigger on DELETE: Decrements counter
- Check constraint: Validates counter matches actual count
- Foreign key cascade: Maintains referential integrity

**Application Layer:**
- Uses denormalized count for display
- Relies on database to maintain consistency
- No manual counter manipulation in most code paths
- Periodic validation job detects any drift

### Performance Comparison

**Without counter cache:**
```sql
SELECT p.*, COUNT(c.id) as comment_count
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
GROUP BY p.id
ORDER BY p.created_at DESC
LIMIT 20;
-- Execution time: 450ms (1M posts, 5M comments)
```

**With counter cache:**
```sql
SELECT p.*, p.comment_count
FROM posts p
ORDER BY p.created_at DESC
LIMIT 20;
-- Execution time: 5ms (no JOIN, no GROUP BY)
```

**Performance improvement: 90x faster**

### Consistency Guarantees

1. **Atomicity**: Database triggers execute in same transaction
2. **Validation**: Check constraint prevents invalid states
3. **Monitoring**: Application logs any constraint violations
4. **Recovery**: Periodic job recalculates and fixes any drift
