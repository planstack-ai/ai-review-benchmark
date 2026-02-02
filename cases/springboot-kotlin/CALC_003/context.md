# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    base_price DECIMAL(19,4) NOT NULL,
    currency_code VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE price_adjustments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    adjustment_type VARCHAR(50) NOT NULL,
    adjustment_value DECIMAL(19,4) NOT NULL,
    is_percentage BOOLEAN NOT NULL DEFAULT FALSE,
    effective_date DATE NOT NULL,
    expiry_date DATE,
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
    
    @Column(name = "base_price", nullable = false, precision = 19, scale = 4)
    val basePrice: BigDecimal,
    
    @Column(name = "currency_code", nullable = false, length = 3)
    val currencyCode: String = "USD",
    
    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "price_adjustments")
data class PriceAdjustment(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "product_id", nullable = false)
    val productId: Long,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "adjustment_type", nullable = false)
    val adjustmentType: AdjustmentType,
    
    @Column(name = "adjustment_value", nullable = false, precision = 19, scale = 4)
    val adjustmentValue: BigDecimal,
    
    @Column(name = "is_percentage", nullable = false)
    val isPercentage: Boolean = false,
    
    @Column(name = "effective_date", nullable = false)
    val effectiveDate: LocalDate,
    
    @Column(name = "expiry_date")
    val expiryDate: LocalDate?
)

enum class AdjustmentType {
    DISCOUNT, MARKUP, TAX, SHIPPING
}

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findByCurrencyCode(currencyCode: String): List<Product>
}

@Repository
interface PriceAdjustmentRepository : JpaRepository<PriceAdjustment, Long> {
    fun findByProductIdAndEffectiveDateLessThanEqualAndExpiryDateGreaterThanEqualOrExpiryDateIsNull(
        productId: Long,
        effectiveDate: LocalDate,
        expiryDate: LocalDate
    ): List<PriceAdjustment>
}

object PricingConstants {
    val DEFAULT_ROUNDING_MODE = RoundingMode.HALF_UP
    const val CURRENCY_SCALE = 4
    const val PERCENTAGE_DIVISOR = 100
}

@Service
interface PricingService {
    fun calculateFinalPrice(productId: Long, calculationDate: LocalDate = LocalDate.now()): BigDecimal?
}

data class PriceCalculationResult(
    val productId: Long,
    val basePrice: BigDecimal,
    val adjustments: List<PriceAdjustment>,
    val finalPrice: BigDecimal,
    val currencyCode: String
)
```