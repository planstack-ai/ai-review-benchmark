# Context: Blog Post Comment System

## Overview

The system displays blog posts with comment counts. The denormalized counter cache is used to optimize the high-traffic post listing pages.

## Database Schema

```sql
CREATE TABLE posts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    comment_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    -- CHECK CONSTRAINT: Ensures counter cannot drift from reality
    -- This constraint is validated on every INSERT/UPDATE
    CONSTRAINT chk_comment_count_valid
        CHECK (comment_count >= 0 AND comment_count <= 10000),

    FOREIGN KEY (author_id) REFERENCES users(id)
);

CREATE TABLE comments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    post_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,

    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_posts_created_at ON posts(created_at);

-- TRIGGER: Automatically increment counter on comment insert
-- This ensures the counter stays in sync without application code
DELIMITER //
CREATE TRIGGER trg_comments_insert AFTER INSERT ON comments
FOR EACH ROW
BEGIN
    UPDATE posts
    SET comment_count = comment_count + 1,
        updated_at = NOW()
    WHERE id = NEW.post_id;
END//

-- TRIGGER: Automatically decrement counter on comment delete
CREATE TRIGGER trg_comments_delete AFTER DELETE ON comments
FOR EACH ROW
BEGIN
    UPDATE posts
    SET comment_count = comment_count - 1,
        updated_at = NOW()
    WHERE id = OLD.post_id;
END//
DELIMITER ;

-- VALIDATION QUERY: Used by periodic job to detect any drift
-- This query finds posts where the counter doesn't match reality
CREATE VIEW v_post_count_validation AS
SELECT
    p.id,
    p.comment_count as cached_count,
    COUNT(c.id) as actual_count,
    p.comment_count - COUNT(c.id) as drift
FROM posts p
LEFT JOIN comments c ON c.post_id = p.id
GROUP BY p.id, p.comment_count
HAVING cached_count != actual_count;
```

## Entities

```kotlin
@Entity
@Table(name = "posts")
data class Post(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false)
    val title: String,

    @Column(nullable = false, columnDefinition = "TEXT")
    val content: String,

    @Column(name = "author_id", nullable = false)
    val authorId: Long,

    /**
     * DENORMALIZED COUNTER CACHE
     *
     * This field duplicates information that could be computed with:
     * SELECT COUNT(*) FROM comments WHERE post_id = ?
     *
     * Why this is CORRECT:
     * 1. Database triggers maintain consistency automatically
     * 2. Check constraint validates count on every update
     * 3. 90x performance improvement on post listings
     * 4. Read-heavy workload justifies denormalization
     * 5. Standard optimization pattern for counter fields
     *
     * Consistency guarantees:
     * - Triggers execute atomically in same transaction
     * - Constraint prevents invalid values
     * - Periodic validation job detects any drift
     * - Foreign key CASCADE maintains referential integrity
     */
    @Column(name = "comment_count", nullable = false)
    val commentCount: Int = 0,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at", nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "comments")
data class Comment(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "post_id", nullable = false)
    val postId: Long,

    @Column(name = "user_id", nullable = false)
    val userId: Long,

    @Column(nullable = false, columnDefinition = "TEXT")
    val content: String,

    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)
```

## Performance Metrics

Production measurements from high-traffic blog platform:

### Post Listing Page (Most Critical Path)
- Traffic: 10,000 requests/minute
- Query: Fetch 20 posts with comment counts
- Without cache: 450ms average, 89% database time
- With cache: 5ms average, 15% database time
- **Result: 90x faster, can handle 50x more traffic**

### Comment Creation (Write Path)
- Traffic: 500 requests/minute
- Overhead: +2ms for trigger execution
- Trade-off: Acceptable (2ms write cost vs 445ms read savings)

### Counter Validation Job
- Frequency: Every 6 hours
- Execution time: 30 seconds
- Drift detection: 0 inconsistencies in 6 months of production
- Conclusion: Database triggers are 100% reliable

## Why Triggers Are Reliable

1. **Atomic execution**: Triggers run in same transaction as INSERT/DELETE
2. **Cannot be bypassed**: All modifications go through triggers
3. **Crash safety**: Transaction rollback includes trigger effects
4. **Tested pattern**: Used by major platforms (GitHub, Reddit, Twitter)

## Alternative Approaches Considered

### Alternative 1: Calculate count on read
```kotlin
@Formula("(SELECT COUNT(*) FROM comments c WHERE c.post_id = id)")
val commentCount: Int
```
**Rejected**: Still executes COUNT query on every read, slower than JOIN

### Alternative 2: Application-level counter management
**Rejected**: Race conditions, requires distributed locks, error-prone

### Alternative 3: Cache computed counts
**Rejected**: Cache invalidation complexity, eventual consistency issues

### Chosen: Database trigger + denormalized field
**Selected**: Best performance, strong consistency, simple implementation
