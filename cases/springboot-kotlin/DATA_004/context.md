# Existing Codebase

## Repository

```kotlin
@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findByActiveTrue(): List<Product>
    fun findByNameContaining(name: String): List<Product>  // Should exclude deleted
}
```

## Usage Guidelines

- Use @Where or @SQLRestriction (Hibernate 6.3+) for automatic soft delete filtering
- Apply soft delete filter at entity level for consistency
