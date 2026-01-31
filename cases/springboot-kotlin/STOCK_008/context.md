# Existing Codebase

## Schema

```sql
CREATE TABLE products (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT NOT NULL DEFAULT 0,
    is_bundle BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bundle_components (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bundle_id BIGINT NOT NULL,
    component_product_id BIGINT NOT NULL,
    quantity_required INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bundle_id) REFERENCES products(id),
    FOREIGN KEY (component_product_id) REFERENCES products(id),
    CHECK (quantity_required > 0)
);

CREATE TABLE bundle_sales (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    bundle_id BIGINT NOT NULL,
    quantity_sold INT NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bundle_id) REFERENCES products(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "products")
data class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(nullable = false)
    val name: String,

    @Column(nullable = false, precision = 10, scale = 2)
    val price: BigDecimal,

    @Column(name = "stock_quantity", nullable = false)
    var stockQuantity: Int,

    @Column(name = "is_bundle", nullable = false)
    val isBundle: Boolean = false,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "bundle_components")
data class BundleComponent(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "bundle_id", nullable = false)
    val bundleId: Long,

    @Column(name = "component_product_id", nullable = false)
    val componentProductId: Long,

    @field:Min(1)
    @Column(name = "quantity_required", nullable = false)
    val quantityRequired: Int,

    @CreationTimestamp
    @Column(name = "created_at")
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "bundle_sales")
data class BundleSale(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,

    @Column(name = "bundle_id", nullable = false)
    val bundleId: Long,

    @Column(name = "quantity_sold", nullable = false)
    val quantitySold: Int,

    @CreationTimestamp
    @Column(name = "sale_date")
    val saleDate: LocalDateTime = LocalDateTime.now()
)

@Repository
interface ProductRepository : JpaRepository<Product, Long> {
    fun findByIdIn(ids: List<Long>): List<Product>
    fun findByIsBundle(isBundle: Boolean): List<Product>
}

@Repository
interface BundleComponentRepository : JpaRepository<BundleComponent, Long> {
    fun findByBundleId(bundleId: Long): List<BundleComponent>
    fun findByComponentProductId(componentProductId: Long): List<BundleComponent>
}

@Repository
interface BundleSaleRepository : JpaRepository<BundleSale, Long> {
    fun findByBundleIdOrderBySaleDateDesc(bundleId: Long): List<BundleSale>
}

data class BundleAvailabilityRequest(
    val bundleId: Long
)

data class BundleAvailabilityResponse(
    val bundleId: Long,
    val bundleName: String,
    val availableQuantity: Int,
    val isAvailable: Boolean,
    val components: List<ComponentAvailability>
)

data class ComponentAvailability(
    val productId: Long,
    val productName: String,
    val requiredPerBundle: Int,
    val availableStock: Int,
    val maxBundlesFromThisComponent: Int
)

data class CreateBundleRequest(
    val name: String,
    val price: BigDecimal,
    val components: List<BundleComponentRequest>
)

data class BundleComponentRequest(
    val productId: Long,
    val quantityRequired: Int
)
```
