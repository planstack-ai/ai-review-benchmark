# Existing Codebase

## Problem Scenario

```java
// After adding loyaltyPoints column, existing rows have NULL
Customer customer = customerRepository.findById(id).get();
int points = customer.getLoyaltyPoints();  // NullPointerException!

// Or in calculations
int newPoints = customer.getLoyaltyPoints() + earnedPoints;  // NPE!
```

## Migration Script

```sql
-- Adding new column
ALTER TABLE customers ADD COLUMN loyalty_points INTEGER;
-- Missing: DEFAULT 0 NOT NULL
-- Missing: UPDATE customers SET loyalty_points = 0 WHERE loyalty_points IS NULL;
```

## Service Using Points

```java
@Service
public class LoyaltyService {
    public int calculateDiscount(Customer customer) {
        int points = customer.getLoyaltyPoints();
        return points / 100;  // 100 points = $1 discount
    }

    public void addPoints(Customer customer, int orderTotal) {
        int currentPoints = customer.getLoyaltyPoints();  // NPE risk
        int earned = orderTotal / 10;
        customer.setLoyaltyPoints(currentPoints + earned);
    }
}
```

## Usage Guidelines

- Always define sensible defaults for new columns
- Use @Column(nullable = false) with @ColumnDefault
- Handle NULL explicitly in entity or use primitive types with defaults
- Migration scripts should set default values for existing rows
