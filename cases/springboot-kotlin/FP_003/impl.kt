package com.example.banking.service

import com.example.banking.entity.Account
import com.example.banking.entity.Transaction
import com.example.banking.entity.TransactionType
import com.example.banking.repository.AccountRepository
import com.example.banking.repository.TransactionRepository
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal

/**
 * This is a CORRECTLY implemented transaction service with proper authorization.
 * No bugs - should NOT trigger any critical or major issues.
 */
@Service
@Transactional
class TransactionService(
    private val transactionRepository: TransactionRepository,
    private val accountRepository: AccountRepository,
    private val accountService: AccountService
) {

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun getAccountTransactions(accountId: Long): List<Transaction> {
        validateAccountExists(accountId)
        return transactionRepository.findByAccountIdOrderByCreatedAtDesc(accountId)
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun getAccountTransactionsPaged(accountId: Long, pageable: Pageable): Page<Transaction> {
        validateAccountExists(accountId)
        return transactionRepository.findByAccountId(accountId, pageable)
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun createDeposit(accountId: Long, amount: BigDecimal, description: String): Transaction {
        validateTransactionAmount(amount)
        val account = getValidatedAccount(accountId)

        val transaction = createTransaction(accountId, amount, TransactionType.DEPOSIT, description)
        updateAccountBalance(account, amount)

        return transactionRepository.save(transaction)
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun createWithdrawal(accountId: Long, amount: BigDecimal, description: String): Transaction {
        validateTransactionAmount(amount)
        val account = getValidatedAccount(accountId)
        validateSufficientBalance(account, amount)

        val transaction = createTransaction(accountId, amount, TransactionType.WITHDRAWAL, description)
        updateAccountBalance(account, amount.negate())

        return transactionRepository.save(transaction)
    }

    @PreAuthorize("(@accountService.isAccountOwnedByUser(#fromAccountId, authentication.principal.id) and @accountService.isAccountOwnedByUser(#toAccountId, authentication.principal.id)) or hasRole('ADMIN')")
    fun createTransfer(
        fromAccountId: Long,
        toAccountId: Long,
        amount: BigDecimal,
        description: String
    ): List<Transaction> {
        validateTransactionAmount(amount)
        val fromAccount = getValidatedAccount(fromAccountId)
        val toAccount = getValidatedAccount(toAccountId)
        validateSufficientBalance(fromAccount, amount)

        val withdrawalTransaction = createTransaction(
            fromAccountId, amount, TransactionType.TRANSFER,
            "Transfer to ${toAccount.accountNumber}: $description"
        )
        val depositTransaction = createTransaction(
            toAccountId, amount, TransactionType.TRANSFER,
            "Transfer from ${fromAccount.accountNumber}: $description"
        )

        updateAccountBalance(fromAccount, amount.negate())
        updateAccountBalance(toAccount, amount)

        val savedWithdrawal = transactionRepository.save(withdrawalTransaction)
        val savedDeposit = transactionRepository.save(depositTransaction)

        return listOf(savedWithdrawal, savedDeposit)
    }

    private fun validateAccountExists(accountId: Long) {
        if (!accountRepository.existsById(accountId)) {
            throw IllegalArgumentException("Account not found: $accountId")
        }
    }

    private fun getValidatedAccount(accountId: Long): Account {
        return accountRepository.findById(accountId)
            .orElseThrow { IllegalArgumentException("Account not found: $accountId") }
    }

    private fun validateTransactionAmount(amount: BigDecimal) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw IllegalArgumentException("Transaction amount must be positive")
        }
    }

    private fun validateSufficientBalance(account: Account, amount: BigDecimal) {
        if (account.balance.compareTo(amount) < 0) {
            throw IllegalArgumentException("Insufficient balance for transaction")
        }
    }

    private fun createTransaction(
        accountId: Long,
        amount: BigDecimal,
        type: TransactionType,
        description: String
    ): Transaction {
        return Transaction().apply {
            this.accountId = accountId
            this.amount = amount
            this.transactionType = type
            this.description = description
        }
    }

    private fun updateAccountBalance(account: Account, amount: BigDecimal) {
        val newBalance = account.balance.add(amount)
        account.balance = newBalance
        accountRepository.save(account)
    }
}
