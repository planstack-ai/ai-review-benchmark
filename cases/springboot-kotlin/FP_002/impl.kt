package com.example.banking.service

import com.example.banking.entity.Account
import com.example.banking.entity.Transaction
import com.example.banking.entity.TransactionType
import com.example.banking.exception.AccountNotFoundException
import com.example.banking.exception.InsufficientFundsException
import com.example.banking.repository.AccountRepository
import com.example.banking.repository.TransactionRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal

/**
 * This is a CORRECTLY implemented banking service.
 * No bugs - should NOT trigger any critical or major issues.
 */
@Service
class BankingService(
    private val accountRepository: AccountRepository,
    private val transactionRepository: TransactionRepository
) {

    @Transactional
    fun transferFunds(
        fromAccountNumber: String,
        toAccountNumber: String,
        amount: BigDecimal,
        description: String
    ): Transaction {
        validateTransferAmount(amount)

        val fromAccount = findAccountWithLock(fromAccountNumber)
        val toAccount = findAccountWithLock(toAccountNumber)

        fromAccount.debit(amount)
        toAccount.credit(amount)

        accountRepository.save(fromAccount)
        accountRepository.save(toAccount)

        return createAndSaveTransaction(fromAccount, toAccount, amount, TransactionType.TRANSFER, description)
    }

    @Transactional
    fun depositFunds(accountNumber: String, amount: BigDecimal, description: String): Transaction {
        validateTransferAmount(amount)

        val account = findAccountWithLock(accountNumber)
        account.credit(amount)
        accountRepository.save(account)

        return createAndSaveTransaction(null, account, amount, TransactionType.DEPOSIT, description)
    }

    @Transactional
    fun withdrawFunds(accountNumber: String, amount: BigDecimal, description: String): Transaction {
        validateTransferAmount(amount)

        val account = findAccountWithLock(accountNumber)
        account.debit(amount)
        accountRepository.save(account)

        return createAndSaveTransaction(account, null, amount, TransactionType.WITHDRAWAL, description)
    }

    @Transactional(readOnly = true)
    fun getAccountTransactionHistory(accountNumber: String): List<Transaction> {
        val account = accountRepository.findByAccountNumber(accountNumber)
            .orElseThrow { AccountNotFoundException("Account not found: $accountNumber") }

        return transactionRepository.findByFromAccountOrToAccountOrderByCreatedAtDesc(account, account)
    }

    @Transactional(readOnly = true)
    fun getAccountBalance(accountNumber: String): BigDecimal {
        val account = accountRepository.findByAccountNumber(accountNumber)
            .orElseThrow { AccountNotFoundException("Account not found: $accountNumber") }

        return account.balance
    }

    private fun findAccountWithLock(accountNumber: String): Account {
        return accountRepository.findByAccountNumberWithLock(accountNumber)
            .orElseThrow { AccountNotFoundException("Account not found: $accountNumber") }
    }

    private fun validateTransferAmount(amount: BigDecimal?) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw IllegalArgumentException("Transfer amount must be positive")
        }
    }

    private fun createAndSaveTransaction(
        fromAccount: Account?,
        toAccount: Account?,
        amount: BigDecimal,
        type: TransactionType,
        description: String
    ): Transaction {
        val transaction = Transaction().apply {
            this.fromAccount = fromAccount
            this.toAccount = toAccount
            this.amount = amount
            this.transactionType = type
            this.description = description
        }

        return transactionRepository.save(transaction)
    }
}
