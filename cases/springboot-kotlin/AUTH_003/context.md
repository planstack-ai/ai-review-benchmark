# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    total_amount DECIMAL(19,2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "users")
data class User(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(unique = true, nullable = false)
    val username: String,
    
    @Column(nullable = false)
    val email: String,
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val role: UserRole,
    
    @CreationTimestamp
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class UserRole {
    USER, ADMIN
}

@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "user_id", nullable = false)
    val userId: Long,
    
    @Column(nullable = false, precision = 19, scale = 2)
    val totalAmount: BigDecimal,
    
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    val status: OrderStatus,
    
    @CreationTimestamp
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

enum class OrderStatus {
    PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED
}

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findByUsername(username: String): User?
}

@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByUserId(userId: Long): List<Order>
    fun findByUserIdAndStatus(userId: Long, status: OrderStatus): List<Order>
}

@Service
class UserService(private val userRepository: UserRepository) {
    
    fun findByUsername(username: String): User? = userRepository.findByUsername(username)
    
    fun getCurrentUser(): User? {
        val authentication = SecurityContextHolder.getContext().authentication
        return authentication?.name?.let { findByUsername(it) }
    }
    
    fun isAdmin(user: User): Boolean = user.role == UserRole.ADMIN
}

@Service
class OrderService(
    private val orderRepository: OrderRepository,
    private val userService: UserService
) {
    
    fun findById(orderId: Long): Order? = orderRepository.findById(orderId).orElse(null)
    
    fun findUserOrders(userId: Long): List<Order> = orderRepository.findByUserId(userId)
    
    fun isOrderOwner(order: Order, user: User): Boolean = order.userId == user.id
    
    fun canCancelOrder(order: Order): Boolean = order.status in listOf(OrderStatus.PENDING, OrderStatus.CONFIRMED)
}
```