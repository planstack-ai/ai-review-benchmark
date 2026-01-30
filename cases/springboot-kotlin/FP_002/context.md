# Existing Codebase

## Schema

```sql
CREATE TABLE accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    balance DECIMAL(19,2) NOT NULL DEFAULT 0.00,
    account_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_account_id BIGINT,
    to_account_id BIGINT,
    amount DECIMAL(19,2) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_account_id) REFERENCES accounts(id),
    FOREIGN KEY (to_account_id) REFERENCES accounts(id)
);
```

## Entities

```kotlin
@Entity
@Table(name = "accounts")
class Account {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @Column(name = "account_number", unique = true, nullable = false)
    var accountNumber: String = ""

    @Column(name = "balance", nullable = false, precision = 19, scale = 2)
    var balance: BigDecimal = BigDecimal.ZERO

    @Enumerated(EnumType.STRING)
    @Column(name = "account_type", nullable = false)
    var accountType: AccountType? = null

    @CreationTimestamp
    @Column(name = "created_at")
    var createdAt: LocalDateTime? = null

    @UpdateTimestamp
    @Column(name = "updated_at")
    var updatedAt: LocalDateTime? = null

    fun credit(amount: BigDecimal) {
        this.balance = this.balance.add(amount)
    }

    fun debit(amount: BigDecimal) {
        if (this.balance.compareTo(amount) < 0) {
            throw InsufficientFundsException("Insufficient balance")
        }
        this.balance = this.balance.subtract(amount)
    }
}

@Entity
@Table(name = "transactions")
class Transaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "from_account_id")
    var fromAccount: Account? = null

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "to_account_id")
    var toAccount: Account? = null

    @Column(name = "amount", nullable = false, precision = 19, scale = 2)
    var amount: BigDecimal = BigDecimal.ZERO

    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_type", nullable = false)
    var transactionType: TransactionType? = null

    @Column(name = "description")
    var description: String? = null

    @CreationTimestamp
    @Column(name = "created_at")
    var createdAt: LocalDateTime? = null
}

enum class AccountType {
    CHECKING, SAVINGS, BUSINESS
}

enum class TransactionType {
    TRANSFER, DEPOSIT, WITHDRAWAL
}
```

```kotlin
@Repository
interface AccountRepository : JpaRepository<Account, Long> {
    fun findByAccountNumber(accountNumber: String): Optional<Account>

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.id = :id")
    fun findByIdWithLock(id: Long): Optional<Account>

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT a FROM Account a WHERE a.accountNumber = :accountNumber")
    fun findByAccountNumberWithLock(accountNumber: String): Optional<Account>
}

@Repository
interface TransactionRepository : JpaRepository<Transaction, Long> {
    fun findByFromAccountOrToAccountOrderByCreatedAtDesc(
        fromAccount: Account,
        toAccount: Account
    ): List<Transaction>
}
```

```kotlin
class InsufficientFundsException(message: String) : RuntimeException(message)

class AccountNotFoundException(message: String) : RuntimeException(message)
```
