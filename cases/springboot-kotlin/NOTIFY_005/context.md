# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    total_amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE refunds (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    refund_amount DECIMAL(19,2) NOT NULL,
    refund_method VARCHAR(50) NOT NULL,
    reason TEXT,
    processed_by_user_id BIGINT NOT NULL,
    status VARCHAR(50) NOT NULL,
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (processed_by_user_id) REFERENCES users(id)
);

CREATE TABLE refund_notifications (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    refund_id BIGINT NOT NULL,
    recipient_email VARCHAR(255) NOT NULL,
    sent_at TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL,
    FOREIGN KEY (refund_id) REFERENCES refunds(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "users")
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false, unique = true)
    val email: String,

    @Column(name = "full_name", nullable = false)
    val fullName: String,

    @Enumerated(EnumType.STRING)
    val role: UserRole,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "user_id", nullable = false)
    val userId: Long,

    @Column(name = "order_number", nullable = false, unique = true)
    val orderNumber: String,

    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    val totalAmount: BigDecimal,

    @Enumerated(EnumType.STRING)
    var status: OrderStatus,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", insertable = false, updatable = false)
    val user: User? = null
)

@Entity
@Table(name = "refunds")
data class Refund(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    val order: Order,

    @Column(name = "refund_amount", nullable = false, precision = 19, scale = 2)
    val refundAmount: BigDecimal,

    @Column(name = "refund_method", nullable = false)
    val refundMethod: String,

    @Column(columnDefinition = "TEXT")
    val reason: String? = null,

    @Column(name = "processed_by_user_id", nullable = false)
    val processedByUserId: Long,

    @Enumerated(EnumType.STRING)
    var status: RefundStatus,

    @Column(name = "processed_at")
    var processedAt: LocalDateTime? = null,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "refund_notifications")
data class RefundNotification(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "refund_id", nullable = false)
    val refundId: Long,

    @Column(name = "recipient_email", nullable = false)
    val recipientEmail: String,

    @Column(name = "sent_at", nullable = false)
    val sentAt: LocalDateTime,

    @Enumerated(EnumType.STRING)
    val status: NotificationStatus
)

enum class UserRole {
    CUSTOMER, ADMIN, SUPPORT
}

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED, REFUNDED
}

enum class RefundStatus {
    PENDING, APPROVED, PROCESSING, COMPLETED, REJECTED
}

enum class NotificationStatus {
    SENT, FAILED, PENDING
}

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findByEmail(email: String): User?
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByOrderNumber(orderNumber: String): Order?
    fun findByUserId(userId: Long): List<Order>
}

@Repository
interface RefundRepository : JpaRepository<Refund, Long> {
    fun findByOrderId(orderId: Long): List<Refund>
}

@Repository
interface RefundNotificationRepository : JpaRepository<RefundNotification, Long> {
    fun findByRefundId(refundId: Long): List<RefundNotification>
}

interface EmailService {
    fun sendEmail(to: String, subject: String, body: String)
}
```
