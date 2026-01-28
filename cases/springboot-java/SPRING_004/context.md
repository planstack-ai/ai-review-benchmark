# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Entities

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    @Email
    @NotBlank
    private String email;
    
    @Column(name = "first_name", nullable = false)
    @NotBlank
    @Size(min = 1, max = 100)
    private String firstName;
    
    @Column(name = "last_name", nullable = false)
    @NotBlank
    @Size(min = 1, max = 100)
    private String lastName;
    
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$")
    private String phone;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // constructors, getters, setters
}

@Entity
@Table(name = "orders")
public class Order {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "user_id", nullable = false)
    private Long userId;
    
    @Column(name = "total_amount", nullable = false, precision = 10, scale = 2)
    @DecimalMin(value = "0.01")
    private BigDecimal totalAmount;
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private OrderStatus status;
    
    @CreationTimestamp
    @Column(name = "order_date")
    private LocalDateTime orderDate;
    
    // constructors, getters, setters
}

public enum OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}
```

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    boolean existsByEmail(String email);
    List<User> findByFirstNameContainingIgnoreCase(String firstName);
}

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByUserIdOrderByOrderDateDesc(Long userId);
    List<Order> findByStatus(OrderStatus status);
    BigDecimal sumTotalAmountByUserId(Long userId);
}
```

```java
@Service
public interface UserService {
    User createUser(User user);
    User updateUser(Long id, User user);
    Optional<User> findById(Long id);
    Optional<User> findByEmail(String email);
    void deleteUser(Long id);
}

@Service
public interface OrderService {
    Order createOrder(Order order);
    List<Order> getOrdersByUserId(Long userId);
    Order updateOrderStatus(Long orderId, OrderStatus status);
}
```