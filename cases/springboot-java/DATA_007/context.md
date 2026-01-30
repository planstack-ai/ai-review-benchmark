# Existing Codebase

## Problem Scenario

```
Import 100 products from CSV
50 already exist (duplicate SKU)
Report says: "100 products imported"  -- Wrong!
Should say: "50 new, 50 skipped (duplicate)"
```

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    price_cents INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

## Repository

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    Optional<Product> findBySku(String sku);
    boolean existsBySku(String sku);

    @Modifying
    @Query(value = "INSERT INTO products (sku, name, price_cents, created_at) " +
                   "VALUES (:sku, :name, :price, :created) " +
                   "ON DUPLICATE KEY UPDATE name = name",
           nativeQuery = true)
    int upsertProduct(@Param("sku") String sku, @Param("name") String name,
                      @Param("price") int price, @Param("created") LocalDateTime created);
}
```

## Usage Guidelines

- Track insert vs update counts separately
- Use repository methods that return affected row counts
- Validate data before batch insert
- Report accurate statistics to users
