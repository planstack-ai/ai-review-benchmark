# Context: Sales Reporting System

## Database Schema

```sql
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_phone VARCHAR(50),
    billing_address TEXT,
    shipping_address TEXT,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    product_name VARCHAR(255) NOT NULL,
    product_description TEXT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    discount_amount DECIMAL(10, 2)
);
```

## Existing Entity (Large Object)

```kotlin
@Entity
@Table(name = "orders")
data class Order(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    val customerEmail: String,
    val customerName: String,
    val customerPhone: String?,

    @Column(columnDefinition = "TEXT")
    val billingAddress: String?,

    @Column(columnDefinition = "TEXT")
    val shippingAddress: String?,

    val totalAmount: BigDecimal,
    val status: String,
    val paymentMethod: String?,

    @Column(columnDefinition = "TEXT")
    val notes: String?,

    @OneToMany(mappedBy = "order", fetch = FetchType.EAGER)
    val items: List<OrderItem> = emptyList(),

    val createdAt: LocalDateTime = LocalDateTime.now(),
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "order_items")
data class OrderItem(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long? = null,

    @ManyToOne
    @JoinColumn(name = "order_id")
    val order: Order,

    val productName: String,

    @Column(columnDefinition = "TEXT")
    val productDescription: String?,

    val quantity: Int,
    val price: BigDecimal,
    val discountAmount: BigDecimal?
)
```

## Performance Context

- Typical order has 5-10 items
- System has 50,000+ orders
- Each full Order entity loads ~2KB of data including all fields and relationships
- Report only needs 3 fields: id, totalAmount, createdAt (~50 bytes per order)
