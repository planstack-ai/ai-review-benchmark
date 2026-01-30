# Existing Codebase

## Schema

```sql
CREATE TABLE order_items (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INTEGER NOT NULL,
    price_cents INTEGER NOT NULL
    -- Note: Foreign key constraint should be added
);
```

## Usage Guidelines

- Always define foreign key constraints at database level for data integrity
- Use cascade options appropriately in JPA mappings
