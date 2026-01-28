# Existing Codebase

## Schema

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    customer_id BIGINT NOT NULL,
    status VARCHAR(20) NOT NULL,
    total_amount DECIMAL(19,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE order_status_transitions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_status VARCHAR(20) NOT NULL,
    to_status VARCHAR(20) NOT NULL,
    allowed BOOLEAN NOT NULL DEFAULT TRUE
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
    
    @Column(name = "customer_id", nullable = false)
    private Long customerId;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private OrderStatus status;
    
    @Column(name = "total_amount", nullable = false, precision = 19, scale = 2)
    private BigDecimal totalAmount;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // constructors, getters, setters
}

public enum OrderStatus {
    PENDING,
    CONFIRMED,
    PROCESSING,
    SHIPPED,
    DELIVERED,
    CANCELLED,
    REFUNDED
}

@Entity
@Table(name = "order_status_transitions")
public class OrderStatusTransition {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "from_status", nullable = false)
    private OrderStatus fromStatus;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "to_status", nullable = false)
    private OrderStatus toStatus;
    
    @Column(nullable = false)
    private Boolean allowed;
    
    // constructors, getters, setters
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCustomerId(Long customerId);
    List<Order> findByStatus(OrderStatus status);
    Optional<Order> findByIdAndCustomerId(Long id, Long customerId);
}

@Repository
public interface OrderStatusTransitionRepository extends JpaRepository<OrderStatusTransition, Long> {
    Optional<OrderStatusTransition> findByFromStatusAndToStatus(OrderStatus fromStatus, OrderStatus toStatus);
    List<OrderStatusTransition> findByFromStatusAndAllowedTrue(OrderStatus fromStatus);
}

@Service
public interface OrderService {
    Order createOrder(Long customerId, BigDecimal totalAmount);
    Order updateOrderStatus(Long orderId, OrderStatus newStatus);
    List<OrderStatus> getAllowedTransitions(OrderStatus currentStatus);
    boolean isTransitionAllowed(OrderStatus fromStatus, OrderStatus toStatus);
}

public class OrderConstants {
    public static final Map<OrderStatus, Set<OrderStatus>> DEFAULT_TRANSITIONS = Map.of(
        OrderStatus.PENDING, Set.of(OrderStatus.CONFIRMED, OrderStatus.CANCELLED),
        OrderStatus.CONFIRMED, Set.of(OrderStatus.PROCESSING, OrderStatus.CANCELLED),
        OrderStatus.PROCESSING, Set.of(OrderStatus.SHIPPED, OrderStatus.CANCELLED),
        OrderStatus.SHIPPED, Set.of(OrderStatus.DELIVERED),
        OrderStatus.DELIVERED, Set.of(OrderStatus.REFUNDED),
        OrderStatus.CANCELLED, Set.of(),
        OrderStatus.REFUNDED, Set.of()
    );
}
```