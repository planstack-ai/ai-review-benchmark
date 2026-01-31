# Context: Product Management System

## Database Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category_id BIGINT,
    stock_quantity INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT true
);

CREATE TABLE admin_override_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    admin_user VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id BIGINT,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Entities

```kotlin
@Entity
@Table(name = "products")
data class Product(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val name: String,
    val price: BigDecimal,
    val categoryId: Long?,
    var stockQuantity: Int = 0,
    var isActive: Boolean = true,
    val createdBy: String,
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "categories")
data class Category(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val name: String,
    val isActive: Boolean = true
)

@Entity
@Table(name = "admin_override_logs")
data class AdminOverrideLog(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val adminUser: String,
    val operation: String,
    val entityType: String,
    val entityId: Long?,
    val reason: String?,
    val createdAt: LocalDateTime = LocalDateTime.now()
)
```

## Existing Repositories

```kotlin
interface ProductRepository : JpaRepository<Product, Long>
interface CategoryRepository : JpaRepository<Category, Long>
interface AdminOverrideLogRepository : JpaRepository<AdminOverrideLog, Long>
```

## Business Requirements

The product management system requires:
1. **Standard Validation**: Normal operations must validate all business rules
2. **Admin Override**: Authorized admins can bypass business rule validation for:
   - Testing and QA purposes
   - Emergency data fixes
   - Bulk data migration
   - Special promotional products
3. **Authorization Check**: Admin override requires proper role authorization
4. **Audit Trail**: All override operations must be logged with admin identity and reason
5. **Data Integrity**: Even with override, critical data integrity constraints must be maintained

This is a standard enterprise pattern where administrative users need flexibility while maintaining accountability through audit trails.
