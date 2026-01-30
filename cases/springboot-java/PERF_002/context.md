# Existing Codebase

## Schema

```sql
-- Table: orders (contains 1M+ records in production)
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_cents INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_created_at (created_at)
);
```

## Entities

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "total_cents", nullable = false)
    private Integer totalCents;

    @Column(nullable = false)
    private String status;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    // getters and setters
}
```

## Repositories

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findAll();
    Page<Order> findAll(Pageable pageable);
    List<Order> findByStatus(String status);

    @Query("SELECT SUM(o.totalCents) FROM Order o WHERE o.createdAt BETWEEN :start AND :end")
    Long sumTotalCentsByDateRange(@Param("start") LocalDateTime start, @Param("end") LocalDateTime end);
}
```

## Usage Guidelines

- For large datasets, always use pagination with `Pageable` or streaming queries
- Avoid loading entire tables into memory
- Use aggregate queries when only totals/counts are needed
