# SPRING_011: Order and Order Items Management

## Overview

Implement Order entity with proper relationship to OrderItem entities, ensuring data integrity when orders are deleted.

## Requirements

1. Order entity should contain multiple OrderItems
2. Support creating orders with items
3. Handle order deletion properly
4. Ensure child records are managed correctly with parent

## Constraints

- Use JPA/Hibernate for persistence
- Follow Spring Boot 3.2+ conventions
- Use Kotlin data classes appropriately
- Ensure referential integrity

## References

- JPA One-to-Many Relationships
- Cascade Types in JPA
- Orphan Removal in Hibernate
