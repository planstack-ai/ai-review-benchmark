# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE payments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    amount DECIMAL(19,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    transaction_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE inventory (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    reserved_quantity INT NOT NULL DEFAULT 0
);
```

## Entities

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "customer_id", nullable = false)
    val customerId: Long,
    
    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    val totalAmount: BigDecimal,
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: OrderStatus = OrderStatus.PENDING,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "payments")
data class Payment(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "order_id", nullable = false)
    val orderId: Long,
    
    @Column(nullable = false, precision = 19, scale = 2)
    val amount: BigDecimal,
    
    @Column(name = "payment_method", nullable = false)
    val paymentMethod: String,
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: PaymentStatus = PaymentStatus.PENDING,
    
    @Column(name = "transaction_id")
    val transactionId: String? = null,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "inventory")
data class Inventory(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "product_id", nullable = false)
    val productId: Long,
    
    @Column(nullable = false)
    val quantity: Int,
    
    @Column(name = "reserved_quantity", nullable = false)
    val reservedQuantity: Int = 0
)

enum class OrderStatus {
    PENDING, CONFIRMED, CANCELLED, COMPLETED
}

enum class PaymentStatus {
    PENDING, PROCESSING, COMPLETED, FAILED, REFUNDED
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
    fun findByStatus(status: OrderStatus): List<Order>
}

@Repository
interface PaymentRepository : JpaRepository<Payment, Long> {
    fun findByOrderId(orderId: Long): List<Payment>
    fun findByStatus(status: PaymentStatus): List<Payment>
}

@Repository
interface InventoryRepository : JpaRepository<Inventory, Long> {
    fun findByProductId(productId: Long): Inventory?
    
    @Modifying
    @Query("UPDATE Inventory i SET i.reservedQuantity = i.reservedQuantity + :quantity WHERE i.productId = :productId")
    fun reserveQuantity(productId: Long, quantity: Int): Int
    
    @Modifying
    @Query("UPDATE Inventory i SET i.quantity = i.quantity - :quantity, i.reservedQuantity = i.reservedQuantity - :quantity WHERE i.productId = :productId")
    fun confirmReservation(productId: Long, quantity: Int): Int
}

@Service
interface PaymentGatewayService {
    fun processPayment(amount: BigDecimal, paymentMethod: String): PaymentResult
}

data class PaymentResult(
    val success: Boolean,
    val transactionId: String?,
    val errorMessage: String? = null
)

data class OrderRequest(
    val customerId: Long,
    val items: List<OrderItem>,
    val paymentMethod: String
)

data class OrderItem(
    val productId: Long,
    val quantity: Int,
    val unitPrice: BigDecimal
)
```