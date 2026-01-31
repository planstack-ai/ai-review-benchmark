# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
    
    @Column(name = "stock_quantity", nullable = false)
    val stockQuantity: Int,
    
    @Version
    val version: Long = 0,
    
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
    val status: ReservationStatus,
    
    @CreationTimestamp
    @Column(name = "reserved_at")
    val reservedAt: LocalDateTime = LocalDateTime.now(),
    
    @Column(name = "expires_at", nullable = false)
    val expiresAt: LocalDateTime
)

enum class ReservationStatus {
    PENDING, CONFIRMED, CANCELLED, EXPIRED
}

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    fun findByIdWithLock(id: Long): Product?
    
    @Modifying
    @Query("UPDATE Product p SET p.stockQuantity = p.stockQuantity - :quantity WHERE p.id = :id AND p.stockQuantity >= :quantity")
    fun decrementStock(id: Long, quantity: Int): Int
}

@Repository
interface StockReservationRepository : JpaRepository<StockReservation, Long> {
    
    fun findByProductIdAndStatus(productId: Long, status: ReservationStatus): List<StockReservation>
    
    @Query("SELECT SUM(r.quantity) FROM StockReservation r WHERE r.productId = :productId AND r.status = :status")
    fun sumQuantityByProductIdAndStatus(productId: Long, status: ReservationStatus): Int?
    
    @Modifying
    @Query("UPDATE StockReservation r SET r.status = :newStatus WHERE r.expiresAt < :now AND r.status = :currentStatus")
    fun expireReservations(now: LocalDateTime, currentStatus: ReservationStatus, newStatus: ReservationStatus): Int
}

data class StockReservationRequest(
    val productId: Long,
    val quantity: Int,
    val reservationDurationMinutes: Int = 15
)

data class StockReservationResponse(
    val reservationId: Long,
    val productId: Long,
    val quantity: Int,
    val expiresAt: LocalDateTime,
    val success: Boolean,
    val message: String? = null
)

@Service
interface StockReservationService {
    fun reserveStock(request: StockReservationRequest): StockReservationResponse
    fun confirmReservation(reservationId: Long): Boolean
    fun cancelReservation(reservationId: Long): Boolean
}
```