# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    total_stock INT NOT NULL DEFAULT 0,
    reserved_stock INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHECK (reserved_stock <= total_stock)
);

CREATE TABLE stock_reservations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    reserved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE inventory_snapshots (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    total_stock INT NOT NULL,
    reserved_stock INT NOT NULL,
    available_stock INT NOT NULL,
    snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

    @Column(nullable = false, precision = 10, scale = 2)
    val price: BigDecimal,

    @Column(name = "total_stock", nullable = false)
    var totalStock: Int,

    @Column(name = "reserved_stock", nullable = false)
    var reservedStock: Int = 0,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @UpdateTimestamp
    @Column(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "stock_reservations")
data class StockReservation(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "product_id", nullable = false)
    val productId: Long,

    @Column(nullable = false)
    val quantity: Int,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: ReservationStatus,

    @CreationTimestamp
    @Column(name = "reserved_at")
    val reservedAt: LocalDateTime = LocalDateTime.now(),

    @Column(name = "expires_at", nullable = false)
    val expiresAt: LocalDateTime
)

enum class ReservationStatus {
    ACTIVE, CONFIRMED, CANCELLED, EXPIRED
}

@Entity
@Table(name = "inventory_snapshots")
data class InventorySnapshot(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "product_id", nullable = false)
    val productId: Long,

    @Column(name = "total_stock", nullable = false)
    val totalStock: Int,

    @Column(name = "reserved_stock", nullable = false)
    val reservedStock: Int,

    @Column(name = "available_stock", nullable = false)
    val availableStock: Int,

    @CreationTimestamp
    @Column(name = "snapshot_at")
    val snapshotAt: LocalDateTime = LocalDateTime.now()
)

@Repository
interface ProductRepository : JpaRepository<Product, Long> {

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    fun findByIdWithLock(id: Long): Product?

    fun findByIdIn(ids: List<Long>): List<Product>
}

@Repository
interface StockReservationRepository : JpaRepository<StockReservation, Long> {

    fun findByProductIdAndStatus(productId: Long, status: ReservationStatus): List<StockReservation>

    @Query("SELECT SUM(r.quantity) FROM StockReservation r WHERE r.productId = :productId AND r.status = :status")
    fun sumQuantityByProductIdAndStatus(productId: Long, status: ReservationStatus): Int?
}

@Repository
interface InventorySnapshotRepository : JpaRepository<InventorySnapshot, Long> {

    fun findByProductIdOrderBySnapshotAtDesc(productId: Long): List<InventorySnapshot>
}

data class StockAvailabilityRequest(
    val productId: Long
)

data class StockAvailabilityResponse(
    val productId: Long,
    val productName: String,
    val totalStock: Int,
    val reservedStock: Int,
    val availableStock: Int,
    val canPurchase: Boolean
)

data class ReservationRequest(
    val productId: Long,
    val quantity: Int,
    val customerId: Long
)

data class ReservationResponse(
    val reservationId: Long,
    val productId: Long,
    val quantity: Int,
    val expiresAt: LocalDateTime,
    val success: Boolean,
    val message: String? = null
)
```
