# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
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
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: OrderStatus,
    
    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    val totalAmount: BigDecimal,
    
    @OneToMany(mappedBy = "order", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val items: List<OrderItem> = emptyList(),
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "order_items")
data class OrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    val order: Order,
    
    @Column(name = "product_id", nullable = false)
    val productId: Long,
    
    @Column(nullable = false)
    val quantity: Int,
    
    @Column(name = "unit_price", nullable = false, precision = 10, scale = 2)
    val unitPrice: BigDecimal
)

enum class OrderStatus {
    PENDING,
    CONFIRMED,
    PROCESSING,
    SHIPPED,
    DELIVERED,
    CANCELLED
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByStatus(status: OrderStatus): List<Order>
    fun findByCustomerIdAndStatus(customerId: Long, status: OrderStatus): List<Order>
}

@Service
interface OrderService {
    fun createOrder(customerId: Long, items: List<OrderItemRequest>): Order
    fun confirmOrder(orderId: Long): Order
    fun cancelOrder(orderId: Long): Order
    fun getOrder(orderId: Long): Order?
    fun getOrdersByCustomer(customerId: Long): List<Order>
}

data class OrderItemRequest(
    val productId: Long,
    val quantity: Int,
    val unitPrice: BigDecimal
)

@ControllerAdvice
class GlobalExceptionHandler {
    
    @ExceptionHandler(IllegalStateException::class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    fun handleIllegalStateException(ex: IllegalStateException): ErrorResponse {
        return ErrorResponse("INVALID_STATE", ex.message ?: "Invalid state transition")
    }
}

data class ErrorResponse(
    val code: String,
    val message: String,
    val timestamp: LocalDateTime = LocalDateTime.now()
)
```