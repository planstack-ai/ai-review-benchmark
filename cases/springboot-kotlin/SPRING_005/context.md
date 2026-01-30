# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    account_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Entities

```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String username;
    
    @Column(unique = true, nullable = false)
    private String email;
    
    @Column(name = "password_hash", nullable = false)
    private String passwordHash;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "account_status")
    private AccountStatus accountStatus = AccountStatus.ACTIVE;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // constructors, getters, setters
}

@Entity
@Table(name = "accounts")
public class Account {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "user_id", nullable = false)
    private Long userId;
    
    @Column(name = "account_number", unique = true, nullable = false)
    private String accountNumber;
    
    @Enumerated(EnumType.STRING)
    @Column(name = "account_type")
    private AccountType accountType;
    
    @Column(precision = 15, scale = 2)
    private BigDecimal balance = BigDecimal.ZERO;
    
    @Enumerated(EnumType.STRING)
    private AccountStatus status = AccountStatus.ACTIVE;
    
    @CreationTimestamp
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    // constructors, getters, setters
}

public enum AccountStatus {
    ACTIVE, SUSPENDED, CLOSED
}

public enum AccountType {
    CHECKING, SAVINGS, BUSINESS
}
```

```java
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
    Optional<User> findByEmail(String email);
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
}

@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {
    List<Account> findByUserId(Long userId);
    Optional<Account> findByAccountNumber(String accountNumber);
    List<Account> findByUserIdAndStatus(Long userId, AccountStatus status);
}
```

```java
@Service
public interface UserService {
    User createUser(String username, String email, String password);
    User findByUsername(String username);
    User updateUserStatus(Long userId, AccountStatus status);
}

@Service
public interface AccountService {
    Account createAccount(Long userId, AccountType accountType);
    Account findByAccountNumber(String accountNumber);
    List<Account> findUserAccounts(Long userId);
    Account updateAccountStatus(Long accountId, AccountStatus status);
}
```

```java
public class ApiConstants {
    public static final String API_VERSION = "/api/v1";
    public static final String USERS_ENDPOINT = API_VERSION + "/users";
    public static final String ACCOUNTS_ENDPOINT = API_VERSION + "/accounts";
    
    public static final String ERROR_USER_NOT_FOUND = "User not found";
    public static final String ERROR_ACCOUNT_NOT_FOUND = "Account not found";
    public static final String ERROR_INVALID_REQUEST = "Invalid request";
    public static final String ERROR_INTERNAL_SERVER = "Internal server error";
}
```