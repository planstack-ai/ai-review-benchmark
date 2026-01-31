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

CREATE TABLE reservations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    customer_id BIGINT NOT NULL,
    quantity INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
@Table(name = "reservations")
data class Reservation(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "product_id", nullable = false)
    val productId: Long,
    
    @Column(name = "customer_id", nullable = false)
    val customerId: Long,
    
    @Column(nullable = false)
    val quantity: Int,
    
    @Enumerated(EnumType.STRING)
    val status: ReservationStatus = ReservationStatus.PENDING,
    
    @Column(name = "expires_at", nullable = false)
    val expiresAt: LocalDateTime,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
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
interface ReservationRepository : JpaRepository<Reservation, Long> {
    fun findByProductIdAndCustomerId(productId: Long, customerId: Long): List<Reservation>
    fun findByStatusAndExpiresAtBefore(status: ReservationStatus, expiredBefore: LocalDateTime): List<Reservation>
}

@Service
interface StockService {
    fun checkAvailability(productId: Long, quantity: Int): Boolean
    fun reserveStock(productId: Long, customerId: Long, quantity: Int): ReservationResult
}

data class ReservationResult(
    val success: Boolean,
    val reservationId: Long? = null,
    val message: String
)

@Component
class ReservationConstants {
    companion object {
        const val DEFAULT_RESERVATION_DURATION_MINUTES = 15L
        const val MAX_RESERVATION_QUANTITY = 10
    }
}
```