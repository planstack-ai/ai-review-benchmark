# Context: External Order Integration

## Database Schema

```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    external_id VARCHAR(255) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Note: external_id should be unique but constraint might not be added yet
-- CREATE UNIQUE INDEX idx_orders_external_id ON orders(external_id);
```

## Existing Entity

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "external_id", nullable = false)
    val externalId: String,

    val customerEmail: String,
    val totalAmount: BigDecimal,
    val status: String,
    val createdAt: LocalDateTime = LocalDateTime.now()
)
```

## Repository

```kotlin
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByExternalId(externalId: String): Order?
}
```

## Usage Pattern

The external system (e.g., payment gateway, marketplace) may send the same order multiple times due to retries or network issues. The system should process each unique order exactly once.

## Concurrency Scenario

Two concurrent requests arrive with the same external_id:
- Thread A: checks if order exists -> not found
- Thread B: checks if order exists -> not found
- Thread A: creates and saves order
- Thread B: creates and saves order (DUPLICATE!)
