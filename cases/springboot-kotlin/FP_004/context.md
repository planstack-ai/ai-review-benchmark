# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(19,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE order_status_transitions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_status VARCHAR(20) NOT NULL,
    to_status VARCHAR(20) NOT NULL,
    allowed BOOLEAN NOT NULL DEFAULT TRUE
);
```

## Entities

```kotlin
@Entity
@Table(name = "orders")
class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Column(name = "customer_id", nullable = false)
    var customerId: Long? = null

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: OrderStatus? = null

    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    var totalAmount: BigDecimal = BigDecimal.ZERO

    @CreationTimestamp
    @Column(name = "created_at")
    var createdAt: LocalDateTime? = null

    @UpdateTimestamp
    @Column(name = "updated_at")
    var updatedAt: LocalDateTime? = null
}

enum class OrderStatus {
    PENDING,
    CONFIRMED,
    PROCESSING,
    SHIPPED,
    DELIVERED,
    CANCELLED,
    REFUNDED
}

@Entity
@Table(name = "order_status_transitions")
class OrderStatusTransition {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Enumerated(EnumType.STRING)
    @Column(name = "from_status", nullable = false)
    var fromStatus: OrderStatus? = null

    @Enumerated(EnumType.STRING)
    @Column(name = "to_status", nullable = false)
    var toStatus: OrderStatus? = null

    @Column(nullable = false)
    var allowed: Boolean? = null
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByStatus(status: OrderStatus): List<Order>
    fun findByIdAndCustomerId(id: Long, customerId: Long): Optional<Order>
}

@Repository
interface OrderStatusTransitionRepository : JpaRepository<OrderStatusTransition, Long> {
    fun findByFromStatusAndToStatus(fromStatus: OrderStatus, toStatus: OrderStatus): Optional<OrderStatusTransition>
    fun findByFromStatusAndAllowedTrue(fromStatus: OrderStatus): List<OrderStatusTransition>
}

interface OrderService {
    fun createOrder(customerId: Long, totalAmount: BigDecimal): Order
    fun updateOrderStatus(orderId: Long, newStatus: OrderStatus): Order
    fun getAllowedTransitions(currentStatus: OrderStatus): List<OrderStatus>
    fun isTransitionAllowed(fromStatus: OrderStatus, toStatus: OrderStatus): Boolean
}

object OrderConstants {
    val DEFAULT_TRANSITIONS: Map<OrderStatus, Set<OrderStatus>> = mapOf(
        OrderStatus.PENDING to setOf(OrderStatus.CONFIRMED, OrderStatus.CANCELLED),
        OrderStatus.CONFIRMED to setOf(OrderStatus.PROCESSING, OrderStatus.CANCELLED),
        OrderStatus.PROCESSING to setOf(OrderStatus.SHIPPED, OrderStatus.CANCELLED),
        OrderStatus.SHIPPED to setOf(OrderStatus.DELIVERED),
        OrderStatus.DELIVERED to setOf(OrderStatus.REFUNDED),
        OrderStatus.CANCELLED to emptySet(),
        OrderStatus.REFUNDED to emptySet()
    )
}
```
