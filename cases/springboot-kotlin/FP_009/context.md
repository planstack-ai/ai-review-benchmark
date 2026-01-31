# Context: Sales Analytics System

## Database Schema

```sql
CREATE TABLE sales (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    sale_date DATE NOT NULL,
    region VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL
);

CREATE INDEX idx_sales_date ON sales(sale_date);
CREATE INDEX idx_sales_region ON sales(region);
CREATE INDEX idx_sales_product ON sales(product_id);
```

## Entities

```kotlin
@Entity
@Table(name = "sales")
data class Sale(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val productId: Long,
    val customerId: Long,
    val quantity: Int,
    val unitPrice: BigDecimal,
    val totalAmount: BigDecimal,
    val saleDate: LocalDate,
    val region: String,
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "products")
data class Product(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val name: String,
    val category: String
)
```

## Report DTOs

```kotlin
data class SalesReportRow(
    val productId: Long,
    val productName: String,
    val region: String,
    val totalSales: BigDecimal,
    val saleCount: Long,
    val runningTotal: BigDecimal,
    val rankInRegion: Int
)

data class DailySalesRow(
    val saleDate: LocalDate,
    val region: String,
    val dailyTotal: BigDecimal,
    val movingAverage: BigDecimal,
    val percentChange: BigDecimal
)
```

## Business Requirements

The sales analytics system requires:
1. **Performance**: Reports must execute in under 2 seconds for 1M+ sales records
2. **Window Functions**: Calculate running totals, rankings, and moving averages efficiently
3. **Database Features**: Utilize PostgreSQL-specific optimizations and functions
4. **Complex Aggregations**: Multi-level grouping with calculated fields
5. **Real-time Analytics**: Support live dashboard queries without pre-aggregation

## Why Native SQL is Necessary

1. **Window Functions**: JPQL does not support window functions (ROW_NUMBER, RANK, SUM OVER)
2. **Performance**: Native SQL with proper indexes is 10x faster than JPQL for complex aggregations
3. **CTEs**: Common Table Expressions simplify complex queries and improve readability
4. **Database-Specific**: PostgreSQL-specific features like FILTER clause and advanced date functions
5. **Query Plans**: Native SQL allows fine-tuning with database-specific hints

This is a legitimate use case where native SQL is the correct choice for performance-critical analytics.
