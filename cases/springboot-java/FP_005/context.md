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

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Column(name = "base_price", nullable = false, precision = 19, scale = 4)
    private BigDecimal basePrice;
    
    @Enumerated(EnumType.STRING)
    private ProductCategory category;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    // constructors, getters, setters
    public Product() {}
    
    public Product(String name, BigDecimal basePrice, ProductCategory category) {
        this.name = name;
        this.basePrice = basePrice;
        this.category = category;
    }
    
    public Long getId() { return id; }
    public String getName() { return name; }
    public BigDecimal getBasePrice() { return basePrice; }
    public ProductCategory getCategory() { return category; }
    public LocalDateTime getCreatedAt() { return createdAt; }
}

@Entity
@Table(name = "price_adjustments")
public class PriceAdjustment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "product_id", nullable = false)
    private Long productId;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "adjustment_type")
    private AdjustmentType adjustmentType;
    
    @Column(name = "adjustment_value", nullable = false, precision = 19, scale = 4)
    private BigDecimal adjustmentValue;
    
    @Column(name = "effective_date")
    private LocalDate effectiveDate;
    
    // constructors, getters, setters
    public PriceAdjustment() {}
    
    public Long getProductId() { return productId; }
    public AdjustmentType getAdjustmentType() { return adjustmentType; }
    public BigDecimal getAdjustmentValue() { return adjustmentValue; }
    public LocalDate getEffectiveDate() { return effectiveDate; }
}

public enum ProductCategory {
    ELECTRONICS, CLOTHING, BOOKS, HOME_GARDEN
}

public enum AdjustmentType {
    DISCOUNT, MARKUP, SEASONAL
}
```

```java
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByCategory(ProductCategory category);
    
    @Query("SELECT p FROM Product p WHERE p.basePrice BETWEEN :minPrice AND :maxPrice")
    List<Product> findByPriceRange(@Param("minPrice") BigDecimal minPrice, 
                                  @Param("maxPrice") BigDecimal maxPrice);
}

@Repository
public interface PriceAdjustmentRepository extends JpaRepository<PriceAdjustment, Long> {
    List<PriceAdjustment> findByProductIdAndEffectiveDateLessThanEqual(
        Long productId, LocalDate date);
}
```

```java
public final class PricingConstants {
    public static final BigDecimal TAX_RATE = new BigDecimal("0.0875");
    public static final BigDecimal DISCOUNT_THRESHOLD = new BigDecimal("100.00");
    public static final BigDecimal MAX_DISCOUNT_PERCENTAGE = new BigDecimal("0.30");
    public static final int PRICE_SCALE = 4;
    public static final RoundingMode PRICE_ROUNDING = RoundingMode.HALF_UP;
    
    private PricingConstants() {}
}

@Service
public interface PricingService {
    BigDecimal calculateFinalPrice(Long productId, LocalDate effectiveDate);
    BigDecimal applyTax(BigDecimal price);
    BigDecimal calculateDiscount(BigDecimal basePrice, BigDecimal discountPercentage);
}
```