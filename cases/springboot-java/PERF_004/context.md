# Existing Codebase

## Repositories

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findAll();
    List<Order> findByStatus(String status);
    long count();
    long countByStatus(String status);
}

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findAll();
    List<User> findByActiveTrue();
    long count();
    long countByActiveTrue();
}

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Order> findAll();
    List<Product> findByCategoryId(Long categoryId);
    long count();
    long countByCategoryId(Long categoryId);
}
```

## Usage Guidelines

- Use `count()` methods when only totals are needed
- Avoid loading entities into memory just to count them
- Use `@Query` with `SELECT COUNT(*)` for complex count conditions
