# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL
    -- Note: Missing UNIQUE constraint on email
);
```

## Usage Guidelines

- Define unique constraints for business keys (email, username, SKU, etc.)
- Use @Column(unique = true) for single-column uniqueness
