# Existing Codebase

## Schema

```sql
-- Table: customers (contains 5M+ records in production)
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE INDEX idx_customers_email (email)
    -- Note: No index on phone_number or name columns
);
```

## Entity

```java
@Entity
@Table(name = "customers")
public class Customer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @Column(name = "phone_number")
    private String phoneNumber;

    @Column(name = "first_name")
    private String firstName;

    @Column(name = "last_name")
    private String lastName;

    private String address;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    // getters and setters
}
```

## Repository

```java
@Repository
public interface CustomerRepository extends JpaRepository<Customer, Long> {
    Optional<Customer> findByEmail(String email);  // Uses index
    List<Customer> findByPhoneNumber(String phoneNumber);  // No index - full scan
    List<Customer> findByLastNameContaining(String lastName);  // No index - full scan
}
```

## Usage Guidelines

- Ensure frequently queried columns have database indexes
- Use EXPLAIN to verify query plans use indexes
- Consider composite indexes for multi-column queries
