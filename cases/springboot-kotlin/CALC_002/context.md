# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    line_total DECIMAL(10,2) NOT NULL,
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
    
    @Column(name = "subtotal", precision = 10, scale = 2, nullable = false)
    val subtotal: BigDecimal,
    
    @Column(name = "discount_amount", precision = 10, scale = 2)
    val discountAmount: BigDecimal = BigDecimal.ZERO,
    
    @Column(name = "tax_amount", precision = 10, scale = 2)
    val taxAmount: BigDecimal = BigDecimal.ZERO,
    
    @Column(name = "total_amount", precision = 10, scale = 2, nullable = false)
    val totalAmount: BigDecimal,
    
    @Enumerated(EnumType.STRING)
    val status: OrderStatus,
    
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @OneToMany(mappedBy = "order", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val items: List<OrderItem> = emptyList()
)

@Entity
@Table(name = "order_items")
data class OrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id")
    val order: Order,
    
    @Column(name = "product_id", nullable = false)
    val productId: Long,
    
    @Column(nullable = false)
    val quantity: Int,
    
    @Column(name = "unit_price", precision = 10, scale = 2, nullable = false)
    val unitPrice: BigDecimal,
    
    @Column(name = "line_total", precision = 10, scale = 2, nullable = false)
    val lineTotal: BigDecimal
)

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByStatus(status: OrderStatus): List<Order>
}

@Repository
interface OrderItemRepository : JpaRepository<OrderItem, Long> {
    fun findByOrderId(orderId: Long): List<OrderItem>
}

object TaxConstants {
    val STANDARD_TAX_RATE: BigDecimal = BigDecimal("0.10")
    val TAX_SCALE = 2
    val ROUNDING_MODE = RoundingMode.HALF_UP
}

@Service
interface OrderService {
    fun createOrder(customerId: Long, items: List<OrderItemRequest>): Order
    fun calculateOrderTotals(subtotal: BigDecimal, discountAmount: BigDecimal): OrderTotals
    fun findOrderById(id: Long): Order?
}

data class OrderItemRequest(
    val productId: Long,
    val quantity: Int,
    val unitPrice: BigDecimal
)

data class OrderTotals(
    val subtotal: BigDecimal,
    val discountAmount: BigDecimal,
    val taxableAmount: BigDecimal,
    val taxAmount: BigDecimal,
    val totalAmount: BigDecimal
)
```