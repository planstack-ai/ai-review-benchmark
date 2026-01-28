package com.example.banking.service;

import com.example.banking.entity.Account;
import com.example.banking.entity.Transaction;
import com.example.banking.entity.TransactionType;
import com.example.banking.repository.AccountRepository;
import com.example.banking.repository.TransactionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

@Service
@Transactional
public class TransactionService {

    @Autowired
    private TransactionRepository transactionRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private AccountService accountService;

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    public List<Transaction> getAccountTransactions(Long accountId) {
        validateAccountExists(accountId);
        return transactionRepository.findByAccountIdOrderByCreatedAtDesc(accountId);
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    public Page<Transaction> getAccountTransactionsPaged(Long accountId, Pageable pageable) {
        validateAccountExists(accountId);
        return transactionRepository.findByAccountId(accountId, pageable);
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    public Transaction createDeposit(Long accountId, BigDecimal amount, String description) {
        validateTransactionAmount(amount);
        Account account = getValidatedAccount(accountId);
        
        Transaction transaction = createTransaction(accountId, amount, TransactionType.DEPOSIT, description);
        updateAccountBalance(account, amount);
        
        return transactionRepository.save(transaction);
    }

    @PreAuthorize("@accountService.isAccountOwnedByUser(#accountId, authentication.principal.id) or hasRole('ADMIN')")
    public Transaction createWithdrawal(Long accountId, BigDecimal amount, String description) {
        validateTransactionAmount(amount);
        Account account = getValidatedAccount(accountId);
        validateSufficientBalance(account, amount);
        
        Transaction transaction = createTransaction(accountId, amount, TransactionType.WITHDRAWAL, description);
        updateAccountBalance(account, amount.negate());
        
        return transactionRepository.save(transaction);
    }

    @PreAuthorize("(@accountService.isAccountOwnedByUser(#fromAccountId, authentication.principal.id) and @accountService.isAccountOwnedByUser(#toAccountId, authentication.principal.id)) or hasRole('ADMIN')")
    public void createTransfer(Long fromAccountId, Long toAccountId, BigDecimal amount, String description) {
        validateTransactionAmount(amount);
        Account fromAccount = getValidatedAccount(fromAccountId);
        Account toAccount = getValidatedAccount(toAccountId);
        validateSufficientBalance(fromAccount, amount);

        Transaction withdrawalTransaction = createTransaction(fromAccountId, amount, TransactionType.TRANSFER, 
            "Transfer to " + toAccount.getAccountNumber() + ": " + description);
        Transaction depositTransaction = createTransaction(toAccountId, amount, TransactionType.TRANSFER, 
            "Transfer from " + fromAccount.getAccountNumber() + ": " + description);

        updateAccountBalance(fromAccount, amount.negate());
        updateAccountBalance(toAccount, amount);

        transactionRepository.save(withdrawalTransaction);
        transactionRepository.save(depositTransaction);
    }

    private void validateAccountExists(Long accountId) {
        if (!accountRepository.existsById(accountId)) {
            throw new IllegalArgumentException("Account not found: " + accountId);
        }
    }

    private Account getValidatedAccount(Long accountId) {
        return accountRepository.findById(accountId)
            .orElseThrow(() -> new IllegalArgumentException("Account not found: " + accountId));
    }

    private void validateTransactionAmount(BigDecimal amount) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Transaction amount must be positive");
        }
    }

    private void validateSufficientBalance(Account account, BigDecimal amount) {
        if (account.getBalance().compareTo(amount) < 0) {
            throw new IllegalArgumentException("Insufficient balance for transaction");
        }
    }

    private Transaction createTransaction(Long accountId, BigDecimal amount, TransactionType type, String description) {
        Transaction transaction = new Transaction();
        transaction.setAccountId(accountId);
        transaction.setAmount(amount);
        transaction.setTransactionType(type);
        transaction.setDescription(description);
        return transaction;
    }

    private void updateAccountBalance(Account account, BigDecimal amount) {
        BigDecimal newBalance = account.getBalance().add(amount);
        account.setBalance(newBalance);
        accountRepository.save(account);
    }
}