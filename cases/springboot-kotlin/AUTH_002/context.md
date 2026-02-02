# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE carts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE cart_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    cart_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE
);
```

## Entities

```kotlin
@Entity
@Table(name = "users")
data class User(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(unique = true, nullable = false)
    val username: String,
    
    @Column(unique = true, nullable = false)
    val email: String,
    
    @CreationTimestamp
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "carts")
data class Cart(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "user_id", nullable = false)
    val userId: Long,
    
    @OneToMany(mappedBy = "cart", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val items: MutableList<CartItem> = mutableListOf(),
    
    @CreationTimestamp
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    val updatedAt: LocalDateTime = LocalDateTime.now()
) {
    fun getTotalAmount(): BigDecimal = items.sumOf { it.getTotalPrice() }
}

@Entity
@Table(name = "cart_items")
data class CartItem(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cart_id")
    val cart: Cart,
    
    @Column(name = "product_id", nullable = false)
    val productId: Long,
    
    @Column(nullable = false)
    val quantity: Int,
    
    @Column(name = "unit_price", nullable = false, precision = 10, scale = 2)
    val unitPrice: BigDecimal
) {
    fun getTotalPrice(): BigDecimal = unitPrice.multiply(BigDecimal(quantity))
}

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findByUsername(username: String): User?
}

@Repository
interface CartRepository : JpaRepository<Cart, Long> {
    fun findByUserId(userId: Long): Cart?
}

@Repository
interface CartItemRepository : JpaRepository<CartItem, Long>

@Service
interface UserService {
    fun getCurrentUser(): User
    fun findByUsername(username: String): User?
}

@Service
class UserServiceImpl(
    private val userRepository: UserRepository
) : UserService {
    
    override fun getCurrentUser(): User {
        val authentication = SecurityContextHolder.getContext().authentication
        return userRepository.findByUsername(authentication.name)
            ?: throw UsernameNotFoundException("User not found")
    }
    
    override fun findByUsername(username: String): User? {
        return userRepository.findByUsername(username)
    }
}

data class AddItemRequest(
    val productId: Long,
    val quantity: Int
)

data class UpdateItemRequest(
    val quantity: Int
)

@ResponseStatus(HttpStatus.FORBIDDEN)
class UnauthorizedCartAccessException(message: String) : RuntimeException(message)

@ResponseStatus(HttpStatus.NOT_FOUND)
class CartNotFoundException(message: String) : RuntimeException(message)
```