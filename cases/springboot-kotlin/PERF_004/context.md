# Existing Codebase

## Repositories

```kotlin
@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findAll(): List<Order>
    fun findByStatus(status: String): List<Order>
    fun count(): Long
    fun countByStatus(status: String): Long
}

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findAll(): List<User>
    fun findByActiveTrue(): List<User>
    fun count(): Long
    fun countByActiveTrue(): Long
}

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findAll(): List<Product>
    fun count(): Long
}
```

## Usage Guidelines

- Use `count()` methods when only totals are needed
- Avoid loading entities into memory just to count them
