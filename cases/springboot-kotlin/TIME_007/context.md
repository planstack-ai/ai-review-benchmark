# Existing Codebase

## Schema

```sql
CREATE TABLE shipments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    shipping_method VARCHAR(50) NOT NULL,
    ship_date DATE NOT NULL,
    estimated_delivery_date DATE NOT NULL,
    actual_delivery_date DATE,
    status VARCHAR(50) NOT NULL,
    tracking_number VARCHAR(100),
    created_at DATETIME NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE shipping_methods (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    business_days INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE delivery_calendar (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    calendar_date DATE NOT NULL UNIQUE,
    is_business_day BOOLEAN NOT NULL,
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    holiday_name VARCHAR(100)
);
```

## Entities

```kotlin
@Entity
@Table(name = "shipments")
data class Shipment(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "order_id", nullable = false)
    val orderId: Long,

    @Column(name = "shipping_method", nullable = false)
    val shippingMethod: String,

    @Column(name = "ship_date", nullable = false)
    val shipDate: LocalDate,

    @Column(name = "estimated_delivery_date", nullable = false)
    val estimatedDeliveryDate: LocalDate,

    @Column(name = "actual_delivery_date")
    val actualDeliveryDate: LocalDate?,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: ShipmentStatus,

    @Column(name = "tracking_number")
    val trackingNumber: String?,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class ShipmentStatus {
    PENDING, SHIPPED, IN_TRANSIT, OUT_FOR_DELIVERY, DELIVERED, FAILED
}

@Entity
@Table(name = "shipping_methods")
data class ShippingMethod(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val name: String,

    @Column(nullable = false, unique = true)
    val code: String,

    @Column(name = "business_days", nullable = false)
    val businessDays: Int,

    @Column(nullable = false, precision = 10, scale = 2)
    val price: BigDecimal,

    @Column(nullable = false)
    val active: Boolean = true
)

@Entity
@Table(name = "delivery_calendar")
data class DeliveryCalendar(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "calendar_date", nullable = false, unique = true)
    val calendarDate: LocalDate,

    @Column(name = "is_business_day", nullable = false)
    val isBusinessDay: Boolean,

    @Column(name = "is_holiday", nullable = false)
    val isHoliday: Boolean = false,

    @Column(name = "holiday_name")
    val holidayName: String?
)

@Repository
interface ShipmentRepository : JpaRepository<Shipment, Long> {
    fun findByOrderId(orderId: Long): Shipment?
    fun findByStatus(status: ShipmentStatus): List<Shipment>
    fun findByEstimatedDeliveryDate(date: LocalDate): List<Shipment>
}

@Repository
interface ShippingMethodRepository : JpaRepository<ShippingMethod, Long> {
    fun findByCode(code: String): ShippingMethod?
    fun findByActiveTrue(): List<ShippingMethod>
}

@Repository
interface DeliveryCalendarRepository : JpaRepository<DeliveryCalendar, Long> {
    fun findByCalendarDate(date: LocalDate): DeliveryCalendar?
    fun findByCalendarDateBetween(startDate: LocalDate, endDate: LocalDate): List<DeliveryCalendar>
}

@Service
interface ShippingService {
    fun calculateDeliveryDate(shipDate: LocalDate, businessDays: Int): LocalDate
    fun createShipment(orderId: Long, shippingMethodCode: String): Shipment
    fun getShippingEstimate(shippingMethodCode: String): ShippingEstimate
}

object ShippingConstants {
    const val STANDARD_SHIPPING_DAYS = 5
    const val EXPRESS_SHIPPING_DAYS = 2
    const val OVERNIGHT_SHIPPING_DAYS = 1
}

data class ShippingEstimate(
    val methodName: String,
    val businessDays: Int,
    val estimatedDeliveryDate: LocalDate,
    val price: BigDecimal
)
```
