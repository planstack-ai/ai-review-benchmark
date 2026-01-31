# Existing Codebase

## Schema

```sql
CREATE TABLE accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    balance DECIMAL(19,2) NOT NULL DEFAULT 0.00,
    version BIGINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_id BIGINT NOT NULL,
    amount DECIMAL(19,2) NOT NULL,
    transaction_type ENUM('CREDIT', 'DEBIT') NOT NULL,
    reference VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "accounts")
data class Account(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "account_number", unique = true, nullable = false)
    val accountNumber: String,
    
    @Column(name = "balance", precision = 19, scale = 2, nullable = false)
    val balance: BigDecimal = BigDecimal.ZERO,
    
    @Version
    @Column(name = "version", nullable = false)
    val version: Long = 0,
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),
    
    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    val updatedAt: LocalDateTime = LocalDateTime.now()
)

@Entity
@Table(name = "transactions")
data class Transaction(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0,
    
    @Column(name = "account_id", nullable = false)
    val accountId: Long,
    
    @Column(name = "amount", precision = 19, scale = 2, nullable = false)
    val amount: BigDecimal,
    
    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_type", nullable = false)
    val type: TransactionType,
    
    @Column(name = "reference")
    val reference: String? = null,
    
    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now()
)

enum class TransactionType {
    CREDIT, DEBIT
}

@Repository
interface AccountRepository : JpaRepository<Account, Long> {
    fun findByAccountNumber(accountNumber: String): Account?
    
    @Lock(LockModeType.OPTIMISTIC_FORCE_INCREMENT)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    fun findByIdWithLock(id: Long): Account?
}

@Repository
interface TransactionRepository : JpaRepository<Transaction, Long> {
    fun findByAccountIdOrderByCreatedAtDesc(accountId: Long): List<Transaction>
}

@Service
interface AccountService {
    fun getAccount(accountNumber: String): Account?
    fun updateBalance(accountId: Long, amount: BigDecimal, type: TransactionType, reference: String?): Account
}

data class BalanceUpdateRequest(
    val accountNumber: String,
    val amount: BigDecimal,
    val type: TransactionType,
    val reference: String? = null
)

class InsufficientFundsException(message: String) : RuntimeException(message)
class AccountNotFoundException(message: String) : RuntimeException(message)
class ConcurrentUpdateException(message: String) : RuntimeException(message)
```