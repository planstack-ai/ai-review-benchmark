# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_cents INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    price_cents INTEGER NOT NULL,
    -- Note: Foreign key constraint should be added
    -- FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);
```

## Existing Order Entity

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

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItem> items = new ArrayList<>();

    // getters and setters
}
```

## Repository

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    void deleteById(Long id);
}

@Repository
public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {
    List<OrderItem> findByOrderId(Long orderId);
}
```

## Usage Guidelines

- Always define foreign key constraints at database level for data integrity
- Use cascade options appropriately in JPA mappings
- Consider orphanRemoval for parent-child relationships
- Database-level constraints are the last line of defense
