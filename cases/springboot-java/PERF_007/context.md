# Existing Codebase

## Schema

```sql
-- Table: order_items (contains 10M+ records in production)
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    price_cents INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    INDEX idx_order_items_order_id (order_id),
    INDEX idx_order_items_product_id (product_id),
    INDEX idx_order_items_created_at (created_at)
);

-- Table: products
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    category_id BIGINT,
    price_cents INTEGER NOT NULL
);
```

## Repository

```java
@Repository
public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {
    List<OrderItem> findAll();
    List<OrderItem> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);

    @Query("SELECT oi.product.id, SUM(oi.quantity) as totalQty " +
           "FROM OrderItem oi GROUP BY oi.product.id ORDER BY totalQty DESC")
    List<Object[]> findTopSellingProducts(Pageable pageable);

    @Query("SELECT oi.product.category.id, SUM(oi.priceCents * oi.quantity) " +
           "FROM OrderItem oi GROUP BY oi.product.category.id")
    List<Object[]> sumRevenueByCategory();
}
```

## Usage Guidelines

- Use database-level aggregation for SUM, COUNT, AVG operations
- Avoid loading large datasets into memory for aggregation
- Use native queries for complex analytics when needed
