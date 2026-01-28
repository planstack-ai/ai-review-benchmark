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
    
    @Column(name = "currency_code", nullable = false, length = 3)
    private String currencyCode = "USD";
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    @OneToMany(mappedBy = "product", fetch = FetchType.LAZY)
    private List<PriceAdjustment> priceAdjustments = new ArrayList<>();
    
    // constructors, getters, setters
}

@Entity
@Table(name = "price_adjustments")
public class PriceAdjustment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    private Product product;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "adjustment_type", nullable = false)
    private AdjustmentType adjustmentType;
    
    @Column(name = "adjustment_value", nullable = false, precision = 19, scale = 4)
    private BigDecimal adjustmentValue;
    
    @Column(name = "is_percentage", nullable = false)
    private Boolean isPercentage = false;
    
    @Column(name = "effective_date", nullable = false)
    private LocalDate effectiveDate;
    
    // constructors, getters, setters
}

public enum AdjustmentType {
    DISCOUNT, TAX, SURCHARGE, PROMOTION
}

@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {
    Optional<Product> findByIdWithAdjustments(Long id);
    
    @Query("SELECT p FROM Product p LEFT JOIN FETCH p.priceAdjustments pa " +
           "WHERE p.id = :id AND (pa.effectiveDate IS NULL OR pa.effectiveDate <= :date)")
    Optional<Product> findByIdWithActiveAdjustments(@Param("id") Long id, @Param("date") LocalDate date);
}

@Repository
public interface PriceAdjustmentRepository extends JpaRepository<PriceAdjustment, Long> {
    List<PriceAdjustment> findByProductIdAndEffectiveDateLessThanEqual(Long productId, LocalDate date);
}

@Component
public class CurrencyConstants {
    public static final String DEFAULT_CURRENCY = "USD";
    public static final int CURRENCY_SCALE = 4;
    public static final RoundingMode DEFAULT_ROUNDING = RoundingMode.HALF_UP;
    public static final BigDecimal HUNDRED = new BigDecimal("100");
}

@Service
public interface PriceCalculationService {
    BigDecimal calculateFinalPrice(Long productId, LocalDate effectiveDate);
    BigDecimal applyAdjustments(BigDecimal basePrice, List<PriceAdjustment> adjustments);
}
```