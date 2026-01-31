# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    order_date DATE NOT NULL,
    scheduled_processing_date DATE NOT NULL,
    total_amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE processing_schedule (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    processing_date DATE NOT NULL UNIQUE,
    capacity INT NOT NULL,
    orders_scheduled INT NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL
);

CREATE TABLE order_processing_log (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    processing_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    processed_at DATETIME,
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

    @Column(name = "order_number", nullable = false, unique = true)
    val orderNumber: String,

    @Column(name = "order_date", nullable = false)
    val orderDate: LocalDate,

    @Column(name = "scheduled_processing_date", nullable = false)
    val scheduledProcessingDate: LocalDate,

    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    val totalAmount: BigDecimal,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: OrderStatus,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class OrderStatus {
    PENDING, SCHEDULED, PROCESSING, COMPLETED, CANCELLED
}

@Entity
@Table(name = "processing_schedule")
data class ProcessingSchedule(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "processing_date", nullable = false, unique = true)
    val processingDate: LocalDate,

    @Column(nullable = false)
    val capacity: Int,

    @Column(name = "orders_scheduled", nullable = false)
    val ordersScheduled: Int = 0,

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "order_processing_log")
data class OrderProcessingLog(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "order_id", nullable = false)
    val orderId: Long,

    @Column(name = "processing_date", nullable = false)
    val processingDate: LocalDate,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: ProcessingStatus,

    @Column(name = "processed_at")
    val processedAt: LocalDateTime?
)

enum class ProcessingStatus {
    SCHEDULED, IN_PROGRESS, COMPLETED, FAILED
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByScheduledProcessingDate(date: LocalDate): List<Order>
    fun findByOrderNumber(orderNumber: String): Order?
    fun findByStatus(status: OrderStatus): List<Order>
}

@Repository
interface ProcessingScheduleRepository : JpaRepository<ProcessingSchedule, Long> {
    fun findByProcessingDate(date: LocalDate): ProcessingSchedule?
    fun findByProcessingDateBetween(startDate: LocalDate, endDate: LocalDate): List<ProcessingSchedule>
}

@Repository
interface OrderProcessingLogRepository : JpaRepository<OrderProcessingLog, Long> {
    fun findByOrderId(orderId: Long): List<OrderProcessingLog>
    fun findByProcessingDate(date: LocalDate): List<OrderProcessingLog>
}

@Service
interface OrderSchedulingService {
    fun scheduleOrderForNextDay(orderId: Long, currentDate: LocalDate): Order
    fun getNextProcessingDate(currentDate: LocalDate): LocalDate
    fun getProcessingCapacity(date: LocalDate): Int
}

object ProcessingConstants {
    const val DEFAULT_DAILY_CAPACITY = 1000
    const val MAX_PROCESSING_DAYS_AHEAD = 30
}
```
