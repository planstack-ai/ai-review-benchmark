# Existing Codebase

## Entity

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String email;
    private Boolean active;

    @Column(name = "engagement_score")
    private Integer engagementScore;

    @Column(name = "last_active")
    private LocalDateTime lastActive;

    @Column(name = "order_count")
    private Integer orderCount;

    // getters and setters
}
```

## Repository

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByActiveTrue();

    @Modifying
    @Query("UPDATE User u SET u.engagementScore = :score WHERE u.id = :userId")
    void updateEngagementScore(@Param("userId") Long userId, @Param("score") Integer score);

    @Modifying
    @Query("UPDATE User u SET u.engagementScore = :score WHERE u.id IN :userIds")
    void bulkUpdateEngagementScore(@Param("userIds") List<Long> userIds, @Param("score") Integer score);
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    long countByUserId(Long userId);

    @Query("SELECT o.userId, COUNT(o) FROM Order o WHERE o.userId IN :userIds GROUP BY o.userId")
    List<Object[]> countOrdersByUserIds(@Param("userIds") List<Long> userIds);
}
```

## Usage Guidelines

- Use batch operations for bulk updates
- Prefer `IN` clause over individual queries in loops
- Use `@Modifying` with bulk update queries
- Consider chunking for very large datasets
