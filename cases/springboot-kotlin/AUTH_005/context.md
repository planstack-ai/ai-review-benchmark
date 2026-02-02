# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL UNIQUE,
    membership_type VARCHAR(50) NOT NULL DEFAULT 'GUEST',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    regular_price DECIMAL(10,2) NOT NULL,
    member_price DECIMAL(10,2),
    is_member_exclusive BOOLEAN DEFAULT FALSE
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

    @Column(nullable = false, unique = true)
    val email: String,

    @Enumerated(EnumType.STRING)
    @Column(name = "membership_type", nullable = false)
    val membershipType: MembershipType = MembershipType.GUEST,

    @Column(name = "is_active")
    val isActive: Boolean = true
)

enum class MembershipType {
    GUEST, MEMBER, PREMIUM
}

@Entity
@Table(name = "products")
data class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val name: String,

    @Column(name = "regular_price", nullable = false, precision = 10, scale = 2)
    val regularPrice: BigDecimal,

    @Column(name = "member_price", precision = 10, scale = 2)
    val memberPrice: BigDecimal?,

    @Column(name = "is_member_exclusive")
    val isMemberExclusive: Boolean = false
)

@Repository
interface UserRepository : JpaRepository<User, Long> {
    fun findByEmail(email: String): User?
}

@Repository
interface ProductRepository : JpaRepository<Product, Long>

// Security context for getting current user
interface SecurityContext {
    fun getCurrentUser(): User?
    fun isAuthenticated(): Boolean
}

fun MembershipType.isMember(): Boolean =
    this == MembershipType.MEMBER || this == MembershipType.PREMIUM
```
