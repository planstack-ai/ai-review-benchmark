package com.example.banking.service

import com.example.banking.entity.Account
import com.example.banking.entity.Transaction
import com.example.banking.entity.TransactionType
import com.example.banking.repository.AccountRepository
import com.example.banking.repository.TransactionRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.util.List

@Service
@Transactional
class TransactionService {

    @Autowired
    private TransactionRepository transactionRepository

    @Autowired
    private AccountRepository accountRepository

    @Autowired
    private AccountService accountService

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun List<Transaction> getAccountTransactions(accountId: Long) {
        validateAccountExists(accountId)
        return transactionRepository.findByAccountIdOrderByCreatedAtDesc(accountId)
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun Page<Transaction> getAccountTransactionsPaged(accountId: Long, pageable: Pageable) {
        validateAccountExists(accountId)
        return transactionRepository.findByAccountId(accountId, pageable)
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun createDeposit(accountId: Long, amount: BigDecimal, description: String): Transaction {
        validateTransactionAmount(amount)
        Account account = getValidatedAccount(accountId)
        
        Transaction transaction = createTransaction(accountId, amount, TransactionType.DEPOSIT, description)
        updateAccountBalance(account, amount)
        
        return transactionRepository.save(transaction)
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    fun createWithdrawal(accountId: Long, amount: BigDecimal, description: String): Transaction {
        validateTransactionAmount(amount)
        Account account = getValidatedAccount(accountId)
        validateSufficientBalance(account, amount)
        
        Transaction transaction = createTransaction(accountId, amount, TransactionType.WITHDRAWAL, description)
        updateAccountBalance(account, amount.negate())
        
        return transactionRepository.save(transaction)
    }

    @PreAuthorize("(@accountService.isAccountOwnedByUser(#fromAccountId, authentication.principal.id) and @accountService.isAccountOwnedByUser(#toAccountId, authentication.principal.id)) or hasRole('ADMIN')")
    fun createTransfer(fromAccountId: Long, toAccountId: Long, amount: BigDecimal, description: String): {
        validateTransactionAmount(amount)
        Account fromAccount = getValidatedAccount(fromAccountId)
        Account toAccount = getValidatedAccount(toAccountId)
        validateSufficientBalance(fromAccount, amount)

        Transaction withdrawalTransaction = createTransaction(fromAccountId, amount, TransactionType.TRANSFER, 
            "Transfer to " + toAccount.AccountNumber + ": " + description)
        Transaction depositTransaction = createTransaction(toAccountId, amount, TransactionType.TRANSFER, 
            "Transfer from " + fromAccount.AccountNumber + ": " + description)

        updateAccountBalance(fromAccount, amount.negate())
        updateAccountBalance(toAccount, amount)

        transactionRepository.save(withdrawalTransaction)
        transactionRepository.save(depositTransaction)
    }

    private fun validateAccountExists(accountId: Long): {
        if (!accountRepository.existsById(accountId)) {
            throw new IllegalArgumentException("Account not found: " + accountId)
        }
    }

    private fun getValidatedAccount(accountId: Long): Account {
        return accountRepository.findById(accountId)
            .orElseThrow { new IllegalArgumentException("Account not found: " + accountId })
    }

    private fun validateTransactionAmount(amount: BigDecimal): {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Transaction amount must be positive")
        }
    }

    private fun validateSufficientBalance(account: Account, amount: BigDecimal): {
        if (account.Balance.compareTo(amount) < 0) {
            throw new IllegalArgumentException("Insufficient balance for transaction")
        }
    }

    private fun createTransaction(accountId: Long, amount: BigDecimal, type: TransactionType, description: String): Transaction {
        Transaction transaction = new Transaction()
        transaction.setAccountId(accountId)
        transaction.setAmount(amount)
        transaction.setTransactionType(type)
        transaction.setDescription(description)
        return transaction
    }

    private fun updateAccountBalance(account: Account, amount: BigDecimal): {
        BigDecimal newBalance = account.Balance.add(amount)
        account.setBalance(newBalance)
        accountRepository.save(account)
    }
}