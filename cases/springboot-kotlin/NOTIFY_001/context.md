# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_email VARCHAR(255) NOT NULL,
    total_amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(19,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE notification_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
    
    @Column(name = "customer_email", nullable = false)
    val customerEmail: String,
    
    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    val totalAmount: BigDecimal,
    
    @Enumerated(EnumType.STRING)
    val status: OrderStatus,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now(),
    
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
    
    @Column(name = "product_name", nullable = false)
    val productName: String,
    
    val quantity: Int,
    
    @Column(name = "unit_price", nullable = false, precision = 19, scale = 2)
    val unitPrice: BigDecimal
)

@Entity
@Table(name = "notification_logs")
data class NotificationLog(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "order_id", nullable = false)
    val orderId: Long,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "notification_type")
    val notificationType: NotificationType,
    
    @Enumerated(EnumType.STRING)
    val status: NotificationStatus,
    
    @Column(name = "error_message")
    val errorMessage: String? = null,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

enum class NotificationType {
    ORDER_CONFIRMATION, SHIPPING_UPDATE, DELIVERY_CONFIRMATION
}

enum class NotificationStatus {
    PENDING, SENT, FAILED, RETRY
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerEmail(email: String): List<Order>
    fun findByStatus(status: OrderStatus): List<Order>
}

@Repository
interface NotificationLogRepository : JpaRepository<NotificationLog, Long> {
    fun findByOrderIdAndNotificationType(orderId: Long, type: NotificationType): List<NotificationLog>
    fun findByStatusAndNotificationType(status: NotificationStatus, type: NotificationType): List<NotificationLog>
}

interface EmailService {
    fun sendOrderConfirmationEmail(order: Order): Boolean
}

@Service
class EmailServiceImpl : EmailService {
    private val logger = LoggerFactory.getLogger(EmailServiceImpl::class.java)
    
    override fun sendOrderConfirmationEmail(order: Order): Boolean {
        return try {
            // Simulate email sending logic
            Thread.sleep(100)
            if (order.customerEmail.contains("invalid")) {
                throw RuntimeException("Invalid email address")
            }
            logger.info("Order confirmation email sent to ${order.customerEmail}")
            true
        } catch (e: Exception) {
            logger.error("Failed to send email to ${order.customerEmail}: ${e.message}")
            false
        }
    }
}
```