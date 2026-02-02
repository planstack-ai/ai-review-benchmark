# Context: Order Management System

## Database Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

## Existing Code

### Order Entity

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "customer_id", nullable = false)
    val customerId: Long,

    @Column(name = "total_amount", nullable = false)
    val totalAmount: BigDecimal,

    @Column(nullable = false)
    @Enumerated(EnumType.STRING)
    var status: OrderStatus = OrderStatus.PENDING,

    @Column(name = "order_date", nullable = false)
    val orderDate: LocalDate = LocalDate.now(),

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class OrderStatus {
    PENDING, ACTIVE, COMPLETED, CANCELLED
}
```

### Repository

```kotlin
@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByStatus(status: OrderStatus): List<Order>
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByOrderDateBetween(startDate: LocalDate, endDate: LocalDate): List<Order>
}
```
