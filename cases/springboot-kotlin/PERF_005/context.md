# Existing Codebase

## Schema

```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    UNIQUE INDEX idx_customers_email (email)
    -- Note: No index on phone_number or name columns
);
```

## Repository

```kotlin
@Repository
interface CustomerRepository : JpaRepository<Customer, Long> {
    fun findByEmail(email: String): Customer?  // Uses index
    fun findByPhoneNumber(phoneNumber: String): List<Customer>  // No index - full scan
    fun findByLastNameContaining(lastName: String): List<Customer>  // No index - full scan
}
```

## Usage Guidelines

- Ensure frequently queried columns have database indexes
- Use EXPLAIN to verify query plans use indexes
