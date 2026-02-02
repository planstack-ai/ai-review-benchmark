# Existing Codebase

## Schema

```sql
CREATE TABLE deliveries (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL UNIQUE,
    tracking_number VARCHAR(100),
    carrier VARCHAR(100),
    status VARCHAR(50) NOT NULL,
    estimated_delivery TIMESTAMP,
    actual_delivery TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE delivery_status_history (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    delivery_id BIGINT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100),
    FOREIGN KEY (delivery_id) REFERENCES deliveries(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "deliveries")
data class Delivery(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "order_id", nullable = false, unique = true)
    val orderId: Long,

    @Column(name = "tracking_number")
    var trackingNumber: String? = null,

    var carrier: String? = null,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: DeliveryStatus,

    @Column(name = "estimated_delivery")
    var estimatedDelivery: LocalDateTime? = null,

    @Column(name = "actual_delivery")
    var actualDelivery: LocalDateTime? = null
)

enum class DeliveryStatus {
    PREPARING,      // ordinal = 0
    SHIPPED,        // ordinal = 1
    IN_TRANSIT,     // ordinal = 2
    OUT_FOR_DELIVERY, // ordinal = 3
    DELIVERED       // ordinal = 4
}

@Entity
@Table(name = "delivery_status_history")
data class DeliveryStatusHistory(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "delivery_id", nullable = false)
    val deliveryId: Long,

    @Enumerated(EnumType.STRING)
    @Column(name = "old_status")
    val oldStatus: DeliveryStatus?,

    @Enumerated(EnumType.STRING)
    @Column(name = "new_status", nullable = false)
    val newStatus: DeliveryStatus,

    @Column(name = "changed_at")
    val changedAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "changed_by")
    val changedBy: String?
)

@Repository
interface DeliveryRepository : JpaRepository<Delivery, Long> {
    fun findByOrderId(orderId: Long): Delivery?
}

@Repository
interface DeliveryStatusHistoryRepository : JpaRepository<DeliveryStatusHistory, Long>

class InvalidStatusTransitionException(message: String) : RuntimeException(message)
```
