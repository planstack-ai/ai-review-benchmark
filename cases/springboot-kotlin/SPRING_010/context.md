# Context: Order Event Processing System

## Database Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory (
    product_id BIGINT PRIMARY KEY,
    quantity INT NOT NULL,
    reserved_quantity INT NOT NULL DEFAULT 0
);

CREATE TABLE notifications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    message TEXT NOT NULL,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_analytics (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Existing Code

### Event Classes

```kotlin
data class OrderCreatedEvent(
    val orderId: Long,
    val customerId: Long,
    val productIds: List<Long>,
    val totalAmount: BigDecimal,
    val timestamp: LocalDateTime = LocalDateTime.now()
)
```

### Repository Interfaces

```kotlin
@Repository
interface InventoryRepository : JpaRepository<Inventory, Long> {
    fun findByProductId(productId: Long): Inventory?
}

@Repository
interface NotificationRepository : JpaRepository<Notification, Long>

@Repository
interface OrderAnalyticsRepository : JpaRepository<OrderAnalytics, Long>
```

### Entities

```kotlin
@Entity
@Table(name = "inventory")
data class Inventory(
    @Id
    @Column(name = "product_id")
    val productId: Long,

    @Column(nullable = false)
    var quantity: Int,

    @Column(name = "reserved_quantity", nullable = false)
    var reservedQuantity: Int = 0
)
```
