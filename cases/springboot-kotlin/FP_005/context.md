# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    base_price DECIMAL(19,4) NOT NULL,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE price_adjustments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    product_id BIGINT NOT NULL,
    adjustment_type VARCHAR(50) NOT NULL,
    adjustment_value DECIMAL(19,4) NOT NULL,
    effective_date DATE NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "products")
class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Column(nullable = false)
    var name: String = ""

    @Column(name = "base_price", nullable = false, precision = 19, scale = 4)
    var basePrice: BigDecimal = BigDecimal.ZERO

    @Enumerated(EnumType.STRING)
    var category: ProductCategory? = null

    @CreationTimestamp
    @Column(name = "created_at")
    var createdAt: LocalDateTime? = null
}

@Entity
@Table(name = "price_adjustments")
class PriceAdjustment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Column(name = "product_id", nullable = false)
    var productId: Long? = null

    @Enumerated(EnumType.STRING)
    @Column(name = "adjustment_type")
    var adjustmentType: AdjustmentType? = null

    @Column(name = "adjustment_value", nullable = false, precision = 19, scale = 4)
    var adjustmentValue: BigDecimal = BigDecimal.ZERO

    @Column(name = "effective_date")
    var effectiveDate: LocalDate? = null
}

enum class ProductCategory {
    ELECTRONICS, CLOTHING, BOOKS, HOME_GARDEN
}

enum class AdjustmentType {
    DISCOUNT, MARKUP, SEASONAL
}
```

```kotlin
@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findByCategory(category: ProductCategory): List<Product>

    @Query("SELECT p FROM Product p WHERE p.basePrice BETWEEN :minPrice AND :maxPrice")
    fun findByPriceRange(
        @Param("minPrice") minPrice: BigDecimal,
        @Param("maxPrice") maxPrice: BigDecimal
    ): List<Product>
}

@Repository
interface PriceAdjustmentRepository : JpaRepository<PriceAdjustment, Long> {
    fun findByProductIdAndEffectiveDateLessThanEqual(
        productId: Long,
        date: LocalDate
    ): List<PriceAdjustment>
}
```

```kotlin
object PricingConstants {
    val TAX_RATE: BigDecimal = BigDecimal("0.0875")
    val DISCOUNT_THRESHOLD: BigDecimal = BigDecimal("100.00")
    val MAX_DISCOUNT_PERCENTAGE: BigDecimal = BigDecimal("0.30")
    const val PRICE_SCALE: Int = 4
    val PRICE_ROUNDING: RoundingMode = RoundingMode.HALF_UP
}

interface PricingService {
    fun calculateFinalPrice(productId: Long, effectiveDate: LocalDate): BigDecimal
    fun applyTax(price: BigDecimal): BigDecimal
    fun calculateDiscount(basePrice: BigDecimal, discountPercentage: BigDecimal): BigDecimal
}
```
