# Existing Codebase

## Schema

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    account_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
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
    
    @Enumerated(EnumType.STRING)
    private Role role;
    
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    // getters and setters
}

@Entity
@Table(name = "accounts")
public class Account {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "account_number", unique = true, nullable = false)
    private String accountNumber;
    
    @Column(name = "user_id", nullable = false)
    private Long userId;
    
    @Column(precision = 15, scale = 2)
    private BigDecimal balance;
    
    @Enumerated(EnumType.STRING)
    private AccountType accountType;
    
    @Enumerated(EnumType.STRING)
    private AccountStatus status;
    
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    // getters and setters
}

@Entity
@Table(name = "transactions")
public class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "account_id", nullable = false)
    private Long accountId;
    
    @Column(precision = 15, scale = 2)
    private BigDecimal amount;
    
    @Enumerated(EnumType.STRING)
    private TransactionType transactionType;
    
    private String description;
    
    @CreationTimestamp
    private LocalDateTime createdAt;
    
    // getters and setters
}

public enum Role {
    USER, ADMIN, MANAGER
}

public enum AccountType {
    CHECKING, SAVINGS, BUSINESS
}

public enum AccountStatus {
    ACTIVE, SUSPENDED, CLOSED
}

public enum TransactionType {
    DEPOSIT, WITHDRAWAL, TRANSFER
}

@Repository
public interface AccountRepository extends JpaRepository<Account, Long> {
    List<Account> findByUserId(Long userId);
    Optional<Account> findByAccountNumber(String accountNumber);
    boolean existsByUserIdAndId(Long userId, Long accountId);
}

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long> {
    List<Transaction> findByAccountIdOrderByCreatedAtDesc(Long accountId);
    Page<Transaction> findByAccountId(Long accountId, Pageable pageable);
}

@Service
public interface AccountService {
    List<Account> getUserAccounts(Long userId);
    Account getAccountById(Long accountId);
    boolean isAccountOwnedByUser(Long accountId, Long userId);
}
```