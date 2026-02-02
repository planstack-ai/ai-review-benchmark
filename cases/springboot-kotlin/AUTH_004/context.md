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

CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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
    ADMIN, USER, MODERATOR
}

@Entity
@Table(name = "products")
data class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(nullable = false)
    val name: String,
    
    val description: String? = null,
    
    @Column(nullable = false, precision = 10, scale = 2)
    val price: BigDecimal,
    
    val category: String? = null,
    
    @CreationTimestamp
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findByUsername(username: String): User?
}

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findByCategory(category: String): List<Product>
    fun findByPriceBetween(minPrice: BigDecimal, maxPrice: BigDecimal): List<Product>
}

@Service
interface UserService {
    fun getCurrentUser(): User?
    fun hasRole(user: User, role: UserRole): Boolean
}

@Service
class UserServiceImpl(
    private val userRepository: UserRepository
) : UserService {
    
    override fun getCurrentUser(): User? {
        val authentication = SecurityContextHolder.getContext().authentication
        return authentication?.name?.let { username ->
            userRepository.findByUsername(username)
        }
    }
    
    override fun hasRole(user: User, role: UserRole): Boolean {
        return user.role == role
    }
}

data class ProductUpdateRequest(
    val name: String? = null,
    val description: String? = null,
    val price: BigDecimal? = null,
    val category: String? = null
)

@RestController
@RequestMapping("/api/products")
class ProductController(
    private val productService: ProductService
) {
    
    @GetMapping
    fun getAllProducts(): List<Product> = productService.findAll()
    
    @GetMapping("/{id}")
    fun getProduct(@PathVariable id: Long): Product? = productService.findById(id)
}

@Service
interface ProductService {
    fun findAll(): List<Product>
    fun findById(id: Long): Product?
    fun updateProduct(id: Long, request: ProductUpdateRequest): Product
}
```