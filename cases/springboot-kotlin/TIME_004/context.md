# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    total_amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    delivery_date DATETIME NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(19,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE delivery_routes (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    route_name VARCHAR(100) NOT NULL,
    delivery_date DATE NOT NULL,
    driver_id BIGINT,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL
);
```

## Entities

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "customer_id", nullable = false)
    val customerId: Long,

    @Column(name = "order_number", nullable = false, unique = true)
    val orderNumber: String,

    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    val totalAmount: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: OrderStatus,

    @Column(name = "delivery_date", nullable = false)
    val deliveryDate: LocalDateTime,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

enum class OrderStatus {
    PENDING, CONFIRMED, PROCESSING, SHIPPED, DELIVERED, CANCELLED
}

@Entity
@Table(name = "order_items")
data class OrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "order_id", nullable = false)
    val orderId: Long,

    @Column(name = "product_id", nullable = false)
    val productId: Long,

    @Column(nullable = false)
    val quantity: Int,

    @Column(name = "unit_price", nullable = false, precision = 19, scale = 2)
    val unitPrice: BigDecimal
)

@Entity
@Table(name = "delivery_routes")
data class DeliveryRoute(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "route_name", nullable = false)
    val routeName: String,

    @Column(name = "delivery_date", nullable = false)
    val deliveryDate: LocalDate,

    @Column(name = "driver_id")
    val driverId: Long?,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: RouteStatus,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class RouteStatus {
    PLANNED, ASSIGNED, IN_PROGRESS, COMPLETED
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByStatus(status: OrderStatus): List<Order>
    fun findByOrderNumber(orderNumber: String): Order?
}

@Repository
interface OrderItemRepository : JpaRepository<OrderItem, Long> {
    fun findByOrderId(orderId: Long): List<OrderItem>
}

@Repository
interface DeliveryRouteRepository : JpaRepository<DeliveryRoute, Long> {
    fun findByDeliveryDate(deliveryDate: LocalDate): List<DeliveryRoute>
    fun findByDriverId(driverId: Long): List<DeliveryRoute>
}

@Service
interface OrderService {
    fun createOrder(customerId: Long, items: List<OrderItemRequest>, deliveryDate: LocalDateTime): Order
    fun getOrdersByDeliveryDate(targetDate: LocalDate): List<Order>
    fun updateOrderStatus(orderId: Long, status: OrderStatus): Order
}

object DeliveryConstants {
    const val STANDARD_DELIVERY_DAYS = 3
    const val EXPRESS_DELIVERY_DAYS = 1
    const val MAX_ORDERS_PER_ROUTE = 50
}

data class OrderItemRequest(
    val productId: Long,
    val quantity: Int
)
```
