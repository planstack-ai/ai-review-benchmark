# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    shipping_cost DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(50) NOT NULL,
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

CREATE TABLE shipping_policies (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    policy_name VARCHAR(100) NOT NULL,
    minimum_amount DECIMAL(10,2) NOT NULL,
    shipping_cost DECIMAL(10,2) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
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
    
    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    val totalAmount: BigDecimal,
    
    @Column(name = "shipping_cost", nullable = false, precision = 10, scale = 2)
    var shippingCost: BigDecimal = BigDecimal.ZERO,
    
    @Enumerated(EnumType.STRING)
    val status: OrderStatus,
    
    @OneToMany(mappedBy = "order", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val items: List<OrderItem> = emptyList(),
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now()
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
    
    @Column(name = "unit_price", nullable = false, precision = 10, scale = 2)
    val unitPrice: BigDecimal
) {
    val subtotal: BigDecimal
        get() = unitPrice.multiply(BigDecimal(quantity))
}

@Entity
@Table(name = "shipping_policies")
data class ShippingPolicy(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "policy_name", nullable = false)
    val policyName: String,
    
    @Column(name = "minimum_amount", nullable = false, precision = 10, scale = 2)
    val minimumAmount: BigDecimal,
    
    @Column(name = "shipping_cost", nullable = false, precision = 10, scale = 2)
    val shippingCost: BigDecimal,
    
    @Column(name = "is_active")
    val isActive: Boolean = true
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
interface ShippingPolicyRepository : JpaRepository<ShippingPolicy, Long> {
    fun findByIsActiveTrueOrderByMinimumAmountAsc(): List<ShippingPolicy>
    fun findByMinimumAmountLessThanEqualAndIsActiveTrueOrderByMinimumAmountDesc(amount: BigDecimal): List<ShippingPolicy>
}

@Service
interface ShippingService {
    fun calculateShippingCost(orderAmount: BigDecimal): BigDecimal
    fun applyShippingPolicy(order: Order): Order
}

object ShippingConstants {
    val STANDARD_SHIPPING_COST = BigDecimal("500")
    val FREE_SHIPPING_THRESHOLD = BigDecimal("5000")
}
```