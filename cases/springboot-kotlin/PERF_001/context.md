# Existing Codebase

## Entities

```kotlin
@Entity
@Table(name = "orders")
class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(name = "user_id", nullable = false)
    val userId: Long,

    @Column(name = "total_cents", nullable = false)
    var totalCents: Int = 0,

    @Column(nullable = false)
    var status: String = "pending",

    @OneToMany(mappedBy = "order", cascade = [CascadeType.ALL], fetch = FetchType.LAZY)
    val items: MutableList<OrderItem> = mutableListOf(),

    @Column(name = "created_at", nullable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "order_items")
class OrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "order_id", nullable = false)
    val order: Order,

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "product_id", nullable = false)
    val product: Product,

    @Column(nullable = false)
    val quantity: Int = 1,

    @Column(name = "price_cents", nullable = false)
    val priceCents: Int
)

@Entity
@Table(name = "products")
class Product(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @Column(nullable = false)
    val name: String,

    val description: String? = null,

    @Column(name = "price_cents", nullable = false)
    val priceCents: Int,

    @Column(nullable = false, unique = true)
    val sku: String
)
```

## Repositories

```kotlin
@Repository
interface OrderRepository : JpaRepository<Order, Long> {
    fun findByCreatedAtBetween(start: LocalDateTime, end: LocalDateTime): List<Order>

    @EntityGraph(attributePaths = ["items", "items.product"])
    fun findWithItemsAndProductsById(id: Long): Order?
}
```

## Usage Guidelines

- Use `@EntityGraph` or `JOIN FETCH` in JPQL queries to avoid N+1 queries when iterating over collections and accessing associations.
- Prefer `FetchType.LAZY` for associations and explicitly fetch when needed.
