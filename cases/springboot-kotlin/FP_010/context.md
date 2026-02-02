# Context: User Login Tracking System

## Overview

The system tracks user login timestamps for analytics and security purposes. The bulk update operation is used during scheduled batch processing where performance is critical.

## Database Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_users_last_login ON users(last_login_at);
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

    @Column(nullable = false)
    val email: String,

    @Column(name = "last_login_at")
    var lastLoginAt: LocalDateTime? = null,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at", nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
)

@EntityListeners(AuditingEntityListener::class)
class AuditingEntityListener {
    @PreUpdate
    fun onUpdate(entity: Any) {
        // This listener would add overhead for bulk operations
        // but is NOT needed for simple timestamp updates
        println("Entity updated: $entity")
    }
}
```

## Usage Context

This repository method is called from:

1. **Scheduled batch job** that processes login events from a queue
2. **Analytics service** that updates statistics hourly
3. **Migration scripts** that backfill historical data

In all these contexts:
- No entities are cached in the persistence context
- Subsequent operations read fresh data from database
- Performance is critical (thousands of updates per minute)
- No business logic validation is needed for timestamp updates

## Performance Characteristics

- Without `@Modifying`: Load 10,000 entities = 10,000 SELECT + 10,000 UPDATE queries
- With `@Modifying`: 1 bulk UPDATE query
- Performance improvement: 100x faster for large batches
- Memory usage: 99% reduction (no entity instantiation)

## Why Entity Listeners Are Not Needed

The `lastLoginAt` field is:
- A simple timestamp with no validation logic
- Not referenced by any business rules during update
- Updated independently of other fields
- Not used to trigger side effects (like notifications)
- Purely for analytics and display purposes
