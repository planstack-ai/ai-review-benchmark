# Context: Email Verification System

## Overview

The system manages user email verification status. The boolean field is queried frequently but intentionally left unindexed based on performance analysis.

## Database Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- INTENTIONALLY NO INDEX on email_verified
-- Reason: Low cardinality (2 values) makes index ineffective
--
-- Performance analysis shows:
-- - Table has ~100k rows, ~50% verified, ~50% unverified
-- - Queries typically return 40-60k rows (40-60% of table)
-- - Index would scan ~50k entries then lookup ~50k rows
-- - Sequential scan of 100k rows is faster in this case
-- - Index maintenance overhead would slow down INSERT/UPDATE operations
-- - Database query planner often ignores boolean indexes anyway

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

## Entity

```kotlin
@Entity
@Table(name = "users")
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false, unique = true)
    val username: String,

    @Column(nullable = false, unique = true)
    val email: String,

    @Column(name = "email_verified", nullable = false)
    var emailVerified: Boolean = false,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at", nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
)
```

## Query Patterns

The `email_verified` field is used in several queries:

1. **List unverified users** (for reminder emails) - returns ~50% of table
2. **List verified users** (for feature access) - returns ~50% of table
3. **Count statistics** - aggregates over entire table
4. **Admin dashboard** - displays both groups

All these queries return large result sets, making indexes ineffective.

## Performance Testing Results

Load test on production-like dataset (100,000 users):

### Without Index (Current Implementation)
```
Query: SELECT * FROM users WHERE email_verified = true
Execution time: 45ms (sequential scan)
Rows scanned: 100,000
Rows returned: 50,234
CPU cost: Low (sequential read, cache-friendly)
```

### With Index (Tested but rejected)
```
Query: SELECT * FROM users WHERE email_verified = true
Execution time: 78ms (index scan + table lookups)
Rows scanned: 50,234 (index) + 50,234 (table)
Rows returned: 50,234
CPU cost: High (random I/O, cache-unfriendly)
```

### Write Performance Impact
- Without index: 1,000 INSERTs/sec
- With index: 750 INSERTs/sec (25% slower)

## Database Statistics

```sql
-- Query to analyze cardinality
SELECT
    email_verified,
    COUNT(*) as count,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM users) as percentage
FROM users
GROUP BY email_verified;

-- Results:
-- FALSE: 48,123 (48.1%)
-- TRUE:  51,877 (51.9%)
--
-- Conclusion: Near-perfect 50/50 distribution
-- Selectivity is too low for indexing to be beneficial
```

## References

- PostgreSQL Documentation: "Indexes on boolean columns are rarely useful"
- MySQL Performance Blog: "When NOT to add an index"
- Database indexing rule: Don't index columns with <5% cardinality ratio
