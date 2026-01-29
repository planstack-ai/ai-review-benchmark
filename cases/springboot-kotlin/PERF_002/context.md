# Existing Codebase

## Repository

```kotlin
@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findAll(): List<Order>  // Warning: loads all records
    fun findAll(pageable: Pageable): Page<Order>
    fun findByStatus(status: String): List<Order>
}
```

## Usage Guidelines

- For large datasets, always use pagination with `Pageable` or streaming queries
- Avoid loading entire tables into memory
- Use aggregate queries when only totals/counts are needed
