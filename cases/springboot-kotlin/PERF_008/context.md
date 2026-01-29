# Existing Codebase

## Repository

```kotlin
@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findByActiveTrue(): List<User>

    @Modifying
    @Query("UPDATE User u SET u.engagementScore = :score WHERE u.id = :userId")
    fun updateEngagementScore(@Param("userId") userId: Long, @Param("score") score: Int)

    @Modifying
    @Query("UPDATE User u SET u.engagementScore = :score WHERE u.id IN :userIds")
    fun bulkUpdateEngagementScore(@Param("userIds") userIds: List<Long>, @Param("score") score: Int)
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun countByUserId(userId: Long): Long

    @Query("SELECT o.userId, COUNT(o) FROM Order o WHERE o.userId IN :userIds GROUP BY o.userId")
    fun countOrdersByUserIds(@Param("userIds") userIds: List<Long>): List<Array<Any>>
}
```

## Usage Guidelines

- Use batch operations for bulk updates
- Prefer `IN` clause over individual queries in loops
