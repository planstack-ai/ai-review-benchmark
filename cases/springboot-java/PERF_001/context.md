# Existing Codebase

## Schema

```sql
-- Table: orders
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_cents INTEGER DEFAULT 0 NOT NULL,
    status VARCHAR(50) DEFAULT 'pending' NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_orders_user_id (user_id)
);

-- Table: order_items
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER DEFAULT 1 NOT NULL,
    price_cents INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_order_items_order_id (order_id),
    INDEX idx_order_items_product_id (product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Table: products
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_cents INTEGER NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    INDEX idx_products_sku (sku),
    INDEX idx_products_active (active)
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
    private Integer totalCents = 0;

    @Column(nullable = false)
    private String status = "pending";

    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<OrderItem> items = new ArrayList<>();

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    // getters and setters
}

@Entity
@Table(name = "order_items")
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    private Order order;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;

    @Column(nullable = false)
    private Integer quantity = 1;

    @Column(name = "price_cents", nullable = false)
    private Integer priceCents;

    // getters and setters
}

@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    private String description;

    @Column(name = "price_cents", nullable = false)
    private Integer priceCents;

    @Column(nullable = false, unique = true)
    private String sku;

    @Column(nullable = false)
    private Boolean active = true;

    // getters and setters
}
```

## Repositories

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);

    @EntityGraph(attributePaths = {"items", "items.product"})
    Optional<Order> findWithItemsAndProductsById(Long id);
}
```

## Usage Guidelines

- Use `@EntityGraph` or `JOIN FETCH` in JPQL queries to avoid N+1 queries when iterating over collections and accessing associations.
- Prefer `FetchType.LAZY` for associations and explicitly fetch when needed.
