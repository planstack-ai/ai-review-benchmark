package com.example.banking.service;

import com.example.banking.entity.Account;
import com.example.banking.entity.Transaction;
import com.example.banking.entity.TransactionType;
import com.example.banking.exception.AccountNotFoundException;
import com.example.banking.exception.InsufficientFundsException;
import com.example.banking.repository.AccountRepository;
import com.example.banking.repository.TransactionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
public class BankingService {

    private final AccountRepository accountRepository;
    private final TransactionRepository transactionRepository;

    @Autowired
    public BankingService(AccountRepository accountRepository, TransactionRepository transactionRepository) {
        this.accountRepository = accountRepository;
        this.transactionRepository = transactionRepository;
    }

    @Transactional
    public Transaction transferFunds(String fromAccountNumber, String toAccountNumber, BigDecimal amount, String description) {
        validateTransferAmount(amount);
        
        Account fromAccount = findAccountWithLock(fromAccountNumber);
        Account toAccount = findAccountWithLock(toAccountNumber);
        
        fromAccount.debit(amount);
        toAccount.credit(amount);
        
        accountRepository.save(fromAccount);
        accountRepository.save(toAccount);
        
        return createAndSaveTransaction(fromAccount, toAccount, amount, TransactionType.TRANSFER, description);
    }

    @Transactional
    public Transaction depositFunds(String accountNumber, BigDecimal amount, String description) {
        validateTransferAmount(amount);
        
        Account account = findAccountWithLock(accountNumber);
        account.credit(amount);
        accountRepository.save(account);
        
        return createAndSaveTransaction(null, account, amount, TransactionType.DEPOSIT, description);
    }

    @Transactional
    public Transaction withdrawFunds(String accountNumber, BigDecimal amount, String description) {
        validateTransferAmount(amount);
        
        Account account = findAccountWithLock(accountNumber);
        account.debit(amount);
        accountRepository.save(account);
        
        return createAndSaveTransaction(account, null, amount, TransactionType.WITHDRAWAL, description);
    }

    @Transactional(readOnly = true)
    public List<Transaction> getAccountTransactionHistory(String accountNumber) {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow(() -> new AccountNotFoundException("Account not found: " + accountNumber));
        
        return transactionRepository.findByFromAccountOrToAccountOrderByCreatedAtDesc(account, account);
    }

    @Transactional(readOnly = true)
    public BigDecimal getAccountBalance(String accountNumber) {
        Account account = accountRepository.findByAccountNumber(accountNumber)
                .orElseThrow(() -> new AccountNotFoundException("Account not found: " + accountNumber));
        
        return account.getBalance();
    }

    private Account findAccountWithLock(String accountNumber) {
        return accountRepository.findByAccountNumberWithLock(accountNumber)
                .orElseThrow(() -> new AccountNotFoundException("Account not found: " + accountNumber));
    }

    private void validateTransferAmount(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Transfer amount must be positive");
        }
    }

    private Transaction createAndSaveTransaction(Account fromAccount, Account toAccount, BigDecimal amount, 
                                               TransactionType type, String description) {
        Transaction transaction = new Transaction();
        transaction.setFromAccount(fromAccount);
        transaction.setToAccount(toAccount);
        transaction.setAmount(amount);
        transaction.setTransactionType(type);
        transaction.setDescription(description);
        
        return transactionRepository.save(transaction);
    }
}