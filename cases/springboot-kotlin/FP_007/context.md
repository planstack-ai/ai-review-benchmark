# Context: Order Fulfillment System

## Database Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE order_state_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    from_state VARCHAR(50),
    to_state VARCHAR(50) NOT NULL,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val customerId: Long,
    val totalAmount: BigDecimal,
    @Enumerated(EnumType.STRING)
    var status: OrderStatus,
    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "order_state_history")
data class OrderStateHistory(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val orderId: Long,
    @Enumerated(EnumType.STRING)
    val fromState: OrderStatus?,
    @Enumerated(EnumType.STRING)
    val toState: OrderStatus,
    val reason: String?,
    val createdAt: LocalDateTime = LocalDateTime.now()
)
```

## Existing Repositories

```kotlin
interface OrderRepository : JpaRepository<Order, Long>
interface OrderStateHistoryRepository : JpaRepository<OrderStateHistory, Long>
```

## Business Requirements

The order fulfillment system requires:
1. **Complete State Coverage**: All possible order lifecycle states must be represented
2. **Validated Transitions**: Only valid state transitions should be allowed based on business rules
3. **Audit Trail**: All state changes must be logged for compliance and customer service
4. **Terminal States**: CANCELLED and RETURNED are final states with no further transitions
5. **Flexible Cancellation**: Orders can be cancelled before shipping

This state machine represents real-world order fulfillment complexity where multiple valid paths exist depending on customer actions and business operations.
