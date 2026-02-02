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

CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    base_price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    active BOOLEAN DEFAULT true
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    campaign_id BIGINT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "campaigns")
data class Campaign(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(nullable = false)
    val name: String,
    
    @Column(name = "discount_percentage", nullable = false, precision = 5, scale = 2)
    val discountPercentage: BigDecimal,
    
    @Column(name = "start_date", nullable = false)
    val startDate: LocalDateTime,
    
    @Column(name = "end_date", nullable = false)
    val endDate: LocalDateTime,
    
    @Column(nullable = false)
    val active: Boolean = true,
    
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "products")
data class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(nullable = false)
    val name: String,
    
    @Column(name = "base_price", nullable = false, precision = 10, scale = 2)
    val basePrice: BigDecimal,
    
    val category: String?,
    
    val active: Boolean = true
)

@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "customer_id", nullable = false)
    val customerId: Long,
    
    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    val totalAmount: BigDecimal,
    
    @Column(name = "discount_amount", precision = 10, scale = 2)
    val discountAmount: BigDecimal = BigDecimal.ZERO,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "campaign_id")
    val campaign: Campaign? = null,
    
    @Column(name = "order_date")
    val orderDate: LocalDateTime = LocalDateTime.now()
)
```

```kotlin
@Repository
interface CampaignRepository : JpaRepository<Campaign, Long> {
    fun findByActiveTrue(): List<Campaign>
    fun findByActiveTrueAndStartDateLessThanEqualAndEndDateGreaterThanEqual(
        startDate: LocalDateTime,
        endDate: LocalDateTime
    ): List<Campaign>
}

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findByActiveTrue(): List<Product>
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCustomerId(customerId: Long): List<Order>
}
```

```kotlin
@Service
interface CampaignService {
    fun getActiveCampaigns(): List<Campaign>
    fun calculateDiscount(baseAmount: BigDecimal, campaignId: Long): BigDecimal
}

@Service
interface OrderService {
    fun createOrder(customerId: Long, productIds: List<Long>, campaignId: Long?): Order
    fun calculateOrderTotal(productIds: List<Long>): BigDecimal
}
```