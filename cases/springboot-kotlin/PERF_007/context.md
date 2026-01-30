# Existing Codebase

## Repository

```kotlin
@Repository
interface OrderItemRepository : JpaRepository<OrderItem, Long> {
    fun findAll(): List<OrderItem>  // 10M+ records in production

    @Query("SELECT oi.product.id, SUM(oi.quantity) as totalQty FROM OrderItem oi GROUP BY oi.product.id ORDER BY totalQty DESC")
    fun findTopSellingProducts(pageable: Pageable): List<Array<Any>>
}
```

## Usage Guidelines

- Use database-level aggregation for SUM, COUNT, AVG operations
- Avoid loading large datasets into memory for aggregation
