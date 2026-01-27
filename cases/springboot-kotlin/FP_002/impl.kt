package com.example.banking.service

import com.example.banking.entity.Account
import com.example.banking.entity.Transaction
import com.example.banking.entity.TransactionType
import com.example.banking.exception.AccountNotFoundException
import com.example.banking.exception.InsufficientFundsException
import com.example.banking.repository.AccountRepository
import com.example.banking.repository.TransactionRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.util.List

@Service
class BankingService {

        private val accountRepository: AccountRepository
        private val transactionRepository: TransactionRepository

    @Autowired
    fun BankingService(accountRepository: AccountRepository, transactionRepository: TransactionRepository) {
        accountRepository = accountRepository
        transactionRepository = transactionRepository
    }

    @Transactional
    fun transferFunds(fromAccountNumber: String, toAccountNumber: String, amount: BigDecimal, description: String): Transaction {
        validateTransferAmount(amount)
        
        Account fromAccount = findAccountWithLock(fromAccountNumber)
        Account toAccount = findAccountWithLock(toAccountNumber)
        
        fromAccount.debit(amount)
        toAccount.credit(amount)
        
        accountRepository.save(fromAccount)
        accountRepository.save(toAccount)
        
        return createAndSaveTransaction(fromAccount, toAccount, amount, TransactionType.TRANSFER, description)
    }

    @Transactional
    fun depositFunds(accountNumber: String, amount: BigDecimal, description: String): Transaction {
        validateTransferAmount(amount)
        
        Account account = findAccountWithLock(accountNumber)
        account.credit(amount)
        accountRepository.save(account)
        
        return createAndSaveTransaction(null, account, amount, TransactionType.DEPOSIT, description)
    }

    @Transactional
    fun withdrawFunds(accountNumber: String, amount: BigDecimal, description: String): Transaction {
        validateTransferAmount(amount)
        
        Account account = findAccountWithLock(accountNumber)
        account.debit(amount)
        accountRepository.save(account)
        
        return createAndSaveTransaction(account, null, amount, TransactionType.WITHDRAWAL, description)
    }

    @Transactional(readOnly = true)
    fun List<Transaction> getAccountTransactionHistory(accountNumber: String) {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow { new AccountNotFoundException("Account not found: " + accountNumber })
        
        return transactionRepository.findByFromAccountOrToAccountOrderByCreatedAtDesc(account, account)
    }

    @Transactional(readOnly = true)
    fun getAccountBalance(accountNumber: String): BigDecimal {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow { new AccountNotFoundException("Account not found: " + accountNumber })
        
        return account.Balance
    }

    private fun findAccountWithLock(accountNumber: String): Account {
        return accountRepository.findByAccountNumberWithLock(accountNumber)
                .orElseThrow { new AccountNotFoundException("Account not found: " + accountNumber })
    }

    private fun validateTransferAmount(amount: BigDecimal): {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Transfer amount must be positive")
        }
    }

    private fun Transaction createAndSaveTransaction(fromAccount: Account, toAccount: Account, amount: BigDecimal, 
                                               TransactionType type, String description) {
        Transaction transaction = new Transaction()
        transaction.setFromAccount(fromAccount)
        transaction.setToAccount(toAccount)
        transaction.setAmount(amount)
        transaction.setTransactionType(type)
        transaction.setDescription(description)
        
        return transactionRepository.save(transaction)
    }
}