# Existing Codebase

## Schema

```sql
CREATE TABLE campaigns (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    discount_percentage DECIMAL(5,2) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    campaign_id BIGINT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
```

## Entities

```java
@Entity
@Table(name = "campaigns")
public class Campaign {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String name;
    
    @Column(name = "discount_percentage", nullable = false, precision = 5, scale = 2)
    private BigDecimal discountPercentage;
    
    @Column(name = "start_date", nullable = false)
    private LocalDateTime startDate;
    
    @Column(name = "end_date", nullable = false)
    private LocalDateTime endDate;
    
    @Column(nullable = false)
    private Boolean active = true;
    
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
    
    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal totalAmount;
    
    @Column(name = "discount_amount", precision = 10, scale = 2)
    private BigDecimal discountAmount = BigDecimal.ZERO;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "campaign_id")
    private Campaign campaign;
    
    @Column(name = "order_date")
    private LocalDateTime orderDate;
    
    // constructors, getters, setters
}

@Repository
public interface CampaignRepository extends JpaRepository<Campaign, Long> {
    
    @Query("SELECT c FROM Campaign c WHERE c.active = true AND :currentTime BETWEEN c.startDate AND c.endDate")
    List<Campaign> findActiveCampaignsAt(@Param("currentTime") LocalDateTime currentTime);
    
    Optional<Campaign> findByIdAndActiveTrue(Long id);
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(Long customerId);
}

@Service
public interface TimeService {
    LocalDateTime getCurrentTime();
}

@Service
@Component
public class SystemTimeService implements TimeService {
    @Override
    public LocalDateTime getCurrentTime() {
        return LocalDateTime.now();
    }
}

public final class DiscountConstants {
    public static final BigDecimal HUNDRED = new BigDecimal("100");
    public static final BigDecimal ZERO = BigDecimal.ZERO;
    
    private DiscountConstants() {}
}
```