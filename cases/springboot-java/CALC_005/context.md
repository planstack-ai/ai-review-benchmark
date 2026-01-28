# Existing Codebase

## Schema

```sql
CREATE TABLE tax_rates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    rate_type VARCHAR(50) NOT NULL,
    rate_value DECIMAL(5,4) NOT NULL,
    effective_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    tax_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'PENDING'
);
```

## Entities

```java
@Entity
@Table(name = "tax_rates")
public class TaxRate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "rate_type", nullable = false)
    private String rateType;
    
    @Column(name = "rate_value", nullable = false, precision = 5, scale = 4)
    private BigDecimal rateValue;
    
    @Column(name = "effective_date", nullable = false)
    private LocalDate effectiveDate;
    
    @Column(name = "is_active")
    private Boolean isActive = true;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    // constructors, getters, setters
}

@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "customer_id", nullable = false)
    private Long customerId;
    
    @Column(name = "subtotal", nullable = false, precision = 10, scale = 2)
    private BigDecimal subtotal;
    
    @Column(name = "tax_amount", precision = 10, scale = 2)
    private BigDecimal taxAmount;
    
    @Column(name = "total_amount", precision = 10, scale = 2)
    private BigDecimal totalAmount;
    
    @Column(name = "order_date")
    private LocalDateTime orderDate;
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
    
    // constructors, getters, setters
}

public enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

@Repository
public interface TaxRateRepository extends JpaRepository<TaxRate, Long> {
    
    @Query("SELECT tr FROM TaxRate tr WHERE tr.rateType = :rateType AND tr.isActive = true ORDER BY tr.effectiveDate DESC")
    Optional<TaxRate> findCurrentRateByType(@Param("rateType") String rateType);
    
    List<TaxRate> findByIsActiveTrueOrderByEffectiveDateDesc();
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerIdOrderByOrderDateDesc(Long customerId);
    List<Order> findByStatusOrderByOrderDateDesc(OrderStatus status);
}

@Service
public interface TaxCalculationService {
    BigDecimal calculateTaxAmount(BigDecimal subtotal);
    BigDecimal calculateTotalWithTax(BigDecimal subtotal);
}

public final class TaxConstants {
    public static final String STANDARD_TAX_TYPE = "STANDARD";
    public static final String SALES_TAX_TYPE = "SALES";
    public static final BigDecimal DEFAULT_TAX_RATE = new BigDecimal("0.1000");
    
    private TaxConstants() {}
}
```