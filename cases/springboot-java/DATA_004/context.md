# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price_cents INTEGER NOT NULL,
    sku VARCHAR(100) NOT NULL UNIQUE,
    category_id BIGINT,
    active BOOLEAN DEFAULT TRUE,
    deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL
);

CREATE INDEX idx_products_deleted ON products(deleted);
```

## Repository

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByActiveTrue();
    List<Product> findByNameContaining(String name);
    List<Product> findByCategoryId(Long categoryId);
    Optional<Product> findBySku(String sku);

    // These methods should exclude deleted products but don't
    @Query("SELECT p FROM Product p WHERE p.deleted = false")
    List<Product> findAllActive();
}
```

## Usage Guidelines

- Use @Where or @SQLRestriction (Hibernate 6.3+) for automatic soft delete filtering
- Apply soft delete filter at entity level for consistency
- Provide separate methods for admin access to deleted records
- Consider using @FilterDef for conditional filtering
