# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    available_stock INTEGER NOT NULL DEFAULT 0,
    reserved_stock INTEGER NOT NULL DEFAULT 0,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE stock_reservations (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    reservation_token VARCHAR(36) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## Entities

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;
    
    @Column(name = "available_stock", nullable = false)
    private Integer availableStock;
    
    @Column(name = "reserved_stock", nullable = false)
    private Integer reservedStock = 0;
    
    @Version
    private Long version;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // constructors, getters, setters
}

@Entity
@Table(name = "stock_reservations")
public class StockReservation {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "product_id", nullable = false)
    private Long productId;
    
    @Column(nullable = false)
    private Integer quantity;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ReservationStatus status = ReservationStatus.PENDING;
    
    @Column(name = "reservation_token", nullable = false, unique = true)
    private String reservationToken;
    
    @Column(name = "expires_at", nullable = false)
    private LocalDateTime expiresAt;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    // constructors, getters, setters
}

public enum ReservationStatus {
    PENDING, CONFIRMED, EXPIRED, CANCELLED
}
```

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT p FROM Product p WHERE p.id = :id")
    Optional<Product> findByIdForUpdate(Long id);
    
    @Modifying
    @Query("UPDATE Product p SET p.availableStock = p.availableStock - :quantity, " +
           "p.reservedStock = p.reservedStock + :quantity WHERE p.id = :id")
    int reserveStock(@Param("id") Long id, @Param("quantity") Integer quantity);
}

@Repository
public interface StockReservationRepository extends JpaRepository<StockReservation, Long> {
    
    Optional<StockReservation> findByReservationToken(String token);
    
    List<StockReservation> findByStatusAndExpiresAtBefore(ReservationStatus status, LocalDateTime dateTime);
    
    @Query("SELECT COUNT(r) FROM StockReservation r WHERE r.productId = :productId AND r.status = :status")
    long countByProductIdAndStatus(@Param("productId") Long productId, @Param("status") ReservationStatus status);
}
```

```java
public interface StockService {
    StockReservationResult reserveStock(Long productId, Integer quantity);
    void confirmReservation(String reservationToken);
    void cancelReservation(String reservationToken);
}

public record StockReservationResult(
    boolean success,
    String reservationToken,
    String message,
    LocalDateTime expiresAt
) {}
```