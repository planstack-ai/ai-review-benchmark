# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    -- Note: Missing UNIQUE constraint on email
    -- UNIQUE INDEX idx_users_email (email)
);
```

## Service

```java
@Service
public class UserRegistrationService {
    @Autowired
    private UserRepository userRepository;

    public User registerUser(String email, String password, String firstName, String lastName) {
        // No check for existing email - relies on database constraint
        User user = new User();
        user.setEmail(email);
        user.setPasswordHash(hashPassword(password));
        user.setFirstName(firstName);
        user.setLastName(lastName);
        return userRepository.save(user);
    }
}
```

## Usage Guidelines

- Define unique constraints for business keys (email, username, SKU, etc.)
- Use @Column(unique = true) for single-column uniqueness
- Use @Table(uniqueConstraints = ...) for composite uniqueness
- Always handle DataIntegrityViolationException
