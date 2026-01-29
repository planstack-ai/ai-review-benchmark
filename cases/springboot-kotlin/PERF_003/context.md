# Existing Codebase

## Related Entities

```kotlin
@Entity
class Category(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val name: String,
    val description: String? = null
)

@Entity
class Review(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    @ManyToOne(fetch = FetchType.LAZY)
    val product: Product,
    val rating: Int,
    val comment: String? = null
)

@Entity
class Inventory(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val productId: Long,
    var quantity: Int
)

@Entity
class Supplier(
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,
    val name: String,
    val contactEmail: String
)
```

## Usage Guidelines

- Prefer `FetchType.LAZY` for all associations
- Use `@EntityGraph` or `JOIN FETCH` when associations are needed
- Avoid `FetchType.EAGER` as it loads data unnecessarily in most cases
