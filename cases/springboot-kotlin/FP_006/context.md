# Context: Payment Processing System

## Database Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notification_queue (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    recipient VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    val amount: BigDecimal,
    var status: String,
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "audit_logs")
data class AuditLog(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val entityType: String,
    val entityId: Long,
    val action: String,
    val details: String?,
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "notification_queue")
data class NotificationQueue(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val recipient: String,
    val message: String,
    var status: String = "PENDING",
    val createdAt: LocalDateTime = LocalDateTime.now()
)
```

## Existing Repositories

```kotlin
interface OrderRepository : JpaRepository<Order, Long>
interface AuditLogRepository : JpaRepository<AuditLog, Long>
interface NotificationQueueRepository : JpaRepository<NotificationQueue, Long>
```

## Business Requirements

The payment processing system requires:
1. **Audit Trail Persistence**: All audit logs must be persisted regardless of business operation success/failure for compliance
2. **Notification Guarantee**: Notifications must be queued even if the main operation fails to ensure customer communication
3. **Transaction Independence**: Audit and notification operations must not participate in the main business transaction

This is a standard enterprise pattern where non-business-critical operations (logging, notifications) must have independent transaction boundaries to ensure they complete successfully even when the main operation fails.
