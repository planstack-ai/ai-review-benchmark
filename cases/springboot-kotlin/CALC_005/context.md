# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "products")
data class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(nullable = false)
    val name: String,
    
    @Column(name = "base_price", nullable = false, precision = 10, scale = 2)
    val basePrice: BigDecimal,
    
    @Column(nullable = false)
    val category: String,
    
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "customer_id", nullable = false)
    val customerId: Long,
    
    @Column(name = "order_date")
    val orderDate: LocalDateTime = LocalDateTime.now(),
    
    @Enumerated(EnumType.STRING)
    val status: OrderStatus = OrderStatus.PENDING,
    
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
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id")
    val product: Product,
    
    @Column(nullable = false)
    val quantity: Int,
    
    @Column(name = "unit_price", nullable = false, precision = 10, scale = 2)
    val unitPrice: BigDecimal
)

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findByCategory(category: String): List<Product>
    fun findByBasePriceBetween(minPrice: BigDecimal, maxPrice: BigDecimal): List<Product>
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByStatus(status: OrderStatus): List<Order>
    fun findByOrderDateBetween(startDate: LocalDateTime, endDate: LocalDateTime): List<Order>
}

@Repository
interface OrderItemRepository : JpaRepository<OrderItem, Long> {
    fun findByOrderId(orderId: Long): List<OrderItem>
    fun findByProductId(productId: Long): List<OrderItem>
}

@Service
interface OrderService {
    fun createOrder(customerId: Long, items: List<OrderItemRequest>): Order
    fun calculateOrderTotal(orderId: Long): BigDecimal
    fun updateOrderStatus(orderId: Long, status: OrderStatus): Order
}

data class OrderItemRequest(
    val productId: Long,
    val quantity: Int
)

data class OrderSummary(
    val orderId: Long,
    val subtotal: BigDecimal,
    val taxAmount: BigDecimal,
    val total: BigDecimal
)
```