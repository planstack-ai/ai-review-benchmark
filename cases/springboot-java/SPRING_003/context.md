# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    total_amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(19,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
```

## Entities

```java
@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "customer_name", nullable = false)
    private String customerName;
    
    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    private BigDecimal totalAmount;
    
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
    
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<OrderItem> items = new ArrayList<>();
    
    // constructors, getters, setters
}

@Entity
@Table(name = "order_items")
public class OrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id")
    private Order order;
    
    @Column(name = "product_name", nullable = false)
    private String productName;
    
    @Column(nullable = false)
    private Integer quantity;
    
    @Column(name = "unit_price", nullable = false, precision = 19, scale = 2)
    private BigDecimal unitPrice;
    
    // constructors, getters, setters
}

public enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}
```

```java
@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerNameContainingIgnoreCase(String customerName);
    List<Order> findByStatus(OrderStatus status);
    List<Order> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
    
    @Query("SELECT o FROM Order o WHERE o.totalAmount >= :minAmount")
    List<Order> findOrdersWithMinimumAmount(@Param("minAmount") BigDecimal minAmount);
}

@Repository
public interface OrderItemRepository extends JpaRepository<OrderItem, Long> {
    List<OrderItem> findByOrderId(Long orderId);
    List<OrderItem> findByProductNameContainingIgnoreCase(String productName);
}
```

```java
public interface OrderService {
    Order createOrder(String customerName, List<OrderItemRequest> items);
    Order findById(Long id);
    List<Order> findByCustomerName(String customerName);
    Order updateOrderStatus(Long orderId, OrderStatus status);
    void cancelOrder(Long orderId);
    BigDecimal calculateOrderTotal(List<OrderItemRequest> items);
    List<Order> findOrdersByDateRange(LocalDateTime start, LocalDateTime end);
}

public record OrderItemRequest(String productName, Integer quantity, BigDecimal unitPrice) {}

@Component
public class OrderConstants {
    public static final BigDecimal MINIMUM_ORDER_AMOUNT = new BigDecimal("10.00");
    public static final int MAX_ITEMS_PER_ORDER = 50;
    public static final String DEFAULT_CURRENCY = "USD";
}
```