# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    sku VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE stock_movements (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    movement_type ENUM('IN', 'OUT') NOT NULL,
    quantity INT NOT NULL,
    reference_id VARCHAR(100),
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
    
    @Column(unique = true, nullable = false)
    val sku: String,
    
    @Column(nullable = false)
    val name: String,
    
    @Column(nullable = false, precision = 10, scale = 2)
    val price: BigDecimal,
    
    @Column(name = "stock_quantity", nullable = false)
    val stockQuantity: Int = 0,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "stock_movements")
data class StockMovement(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "product_id", nullable = false)
    val productId: Long,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "movement_type", nullable = false)
    val movementType: MovementType,
    
    @Column(nullable = false)
    val quantity: Int,
    
    @Column(name = "reference_id")
    val referenceId: String? = null,
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class MovementType {
    IN, OUT
}

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findBySku(sku: String): Product?
    
    @Modifying
    @Query("UPDATE Product p SET p.stockQuantity = p.stockQuantity + :quantity WHERE p.id = :productId")
    fun updateStockQuantity(productId: Long, quantity: Int): Int
}

@Repository
interface StockMovementRepository : JpaRepository<StockMovement, Long> {
    fun findByProductIdOrderByCreatedAtDesc(productId: Long): List<StockMovement>
}

interface StockService {
    fun adjustStock(productId: Long, quantity: Int, referenceId: String? = null): Product
    fun getAvailableStock(productId: Long): Int
}

data class StockAdjustmentRequest(
    val productId: Long,
    val quantity: Int,
    val referenceId: String? = null
)

data class StockValidationResult(
    val isValid: Boolean,
    val currentStock: Int,
    val requestedQuantity: Int,
    val resultingStock: Int,
    val errorMessage: String? = null
)

class InsufficientStockException(
    val productId: Long,
    val currentStock: Int,
    val requestedQuantity: Int
) : RuntimeException("Insufficient stock for product $productId. Current: $currentStock, Requested: $requestedQuantity")
```