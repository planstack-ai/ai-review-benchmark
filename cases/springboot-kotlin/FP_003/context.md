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

```kotlin
@Entity
@Table(name = "users")
class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Column(unique = true, nullable = false)
    var username: String = ""

    @Column(unique = true, nullable = false)
    var email: String = ""

    @Enumerated(EnumType.STRING)
    var role: Role? = null

    @CreationTimestamp
    var createdAt: LocalDateTime? = null
}

@Entity
@Table(name = "accounts")
class Account {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Column(name = "account_number", unique = true, nullable = false)
    var accountNumber: String = ""

    @Column(name = "user_id", nullable = false)
    var userId: Long? = null

    @Column(precision = 15, scale = 2)
    var balance: BigDecimal = BigDecimal.ZERO

    @Enumerated(EnumType.STRING)
    var accountType: AccountType? = null

    @Enumerated(EnumType.STRING)
    var status: AccountStatus? = null

    @CreationTimestamp
    var createdAt: LocalDateTime? = null
}

@Entity
@Table(name = "transactions")
class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Column(name = "account_id", nullable = false)
    var accountId: Long? = null

    @Column(precision = 15, scale = 2)
    var amount: BigDecimal = BigDecimal.ZERO

    @Enumerated(EnumType.STRING)
    var transactionType: TransactionType? = null

    var description: String? = null

    @CreationTimestamp
    var createdAt: LocalDateTime? = null
}

enum class Role {
    USER, ADMIN, MANAGER
}

enum class AccountType {
    CHECKING, SAVINGS, BUSINESS
}

enum class AccountStatus {
    ACTIVE, SUSPENDED, CLOSED
}

enum class TransactionType {
    DEPOSIT, WITHDRAWAL, TRANSFER
}

@Repository
interface AccountRepository : JpaRepository<Account, Long> {
    fun findByUserId(userId: Long): List<Account>
    fun findByAccountNumber(accountNumber: String): Optional<Account>
    fun existsByUserIdAndId(userId: Long, accountId: Long): Boolean
}

@Repository
interface TransactionRepository : JpaRepository<Transaction, Long> {
    fun findByAccountIdOrderByCreatedAtDesc(accountId: Long): List<Transaction>
    fun findByAccountId(accountId: Long, pageable: Pageable): Page<Transaction>
}

interface AccountService {
    fun getUserAccounts(userId: Long): List<Account>
    fun getAccountById(accountId: Long): Account
    fun isAccountOwnedByUser(accountId: Long, userId: Long): Boolean
}
```
