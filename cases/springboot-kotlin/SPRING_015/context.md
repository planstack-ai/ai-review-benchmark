# Context: Order Archival and Audit System

## Database Schema

```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    entity_id BIGINT NOT NULL,
    action VARCHAR(50) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP NOT NULL,
    changed_by VARCHAR(100)
);
```

## Existing Entity with Listener

```kotlin
@Entity
@Table(name = "orders")
@EntityListeners(OrderAuditListener::class)
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    val customerEmail: String,
    val totalAmount: BigDecimal,

    var status: String,

    val createdAt: LocalDateTime = LocalDateTime.now(),
    var updatedAt: LocalDateTime = LocalDateTime.now()
)

@Component
class OrderAuditListener(
    private val auditLogRepository: AuditLogRepository
) {
    @PreUpdate
    fun preUpdate(order: Order) {
        // This callback should log status changes to audit_logs table
        auditLogRepository.save(
            AuditLog(
                entityType = "Order",
                entityId = order.id!!,
                action = "UPDATE",
                oldValue = "status: ${order.status}",
                newValue = "status: ARCHIVED",
                changedAt = LocalDateTime.now(),
                changedBy = "system"
            )
        )
    }
}
```

## Audit Log Entity

```kotlin
@Entity
@Table(name = "audit_logs")
data class AuditLog(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    val entityType: String,
    val entityId: Long,
    val action: String,
    val oldValue: String?,
    val newValue: String?,
    val changedAt: LocalDateTime,
    val changedBy: String
)
```

## Compliance Requirement

All status changes must be audited for regulatory compliance. Missing audit logs can result in failed audits and penalties.
