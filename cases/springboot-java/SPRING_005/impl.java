package com.example.benchmark.service;

import com.example.benchmark.dto.PaymentRequest;
import com.example.benchmark.dto.PaymentResponse;
import com.example.benchmark.entity.Payment;
import com.example.benchmark.entity.Account;
import com.example.benchmark.repository.PaymentRepository;
import com.example.benchmark.repository.AccountRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

@Service
@Transactional
public class PaymentProcessingService {

    @Autowired
    private PaymentRepository paymentRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private NotificationService notificationService;

    public ResponseEntity<?> processPayment(PaymentRequest request) {
        try {
            validatePaymentRequest(request);
            
            Account sourceAccount = getAccountById(request.getSourceAccountId());
            Account targetAccount = getAccountById(request.getTargetAccountId());
            
            BigDecimal amount = request.getAmount();
            
            if (hasInsufficientFunds(sourceAccount, amount)) {
                return ResponseEntity.badRequest().body("Insufficient funds available");
            }
            
            Payment payment = createPayment(request, sourceAccount, targetAccount);
            executeTransfer(sourceAccount, targetAccount, amount);
            
            Payment savedPayment = paymentRepository.save(payment);
            notificationService.sendPaymentConfirmation(savedPayment);
            
            PaymentResponse response = buildPaymentResponse(savedPayment);
            return ResponseEntity.ok(response);
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    private void validatePaymentRequest(PaymentRequest request) {
        if (request.getAmount() == null || request.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Payment amount must be positive");
        }
        
        if (request.getSourceAccountId() == null || request.getTargetAccountId() == null) {
            throw new IllegalArgumentException("Source and target account IDs are required");
        }
        
        if (request.getSourceAccountId().equals(request.getTargetAccountId())) {
            throw new IllegalArgumentException("Source and target accounts cannot be the same");
        }
    }

    private Account getAccountById(Long accountId) {
        Optional<Account> account = accountRepository.findById(accountId);
        if (!account.isPresent()) {
            throw new RuntimeException("Account not found with ID: " + accountId);
        }
        
        if (!account.get().isActive()) {
            throw new RuntimeException("Account is inactive: " + accountId);
        }
        
        return account.get();
    }

    private boolean hasInsufficientFunds(Account account, BigDecimal amount) {
        BigDecimal availableBalance = calculateAvailableBalance(account);
        return availableBalance.compareTo(amount) < 0;
    }

    private BigDecimal calculateAvailableBalance(Account account) {
        BigDecimal currentBalance = account.getBalance();
        BigDecimal reservedAmount = account.getReservedAmount();
        return currentBalance.subtract(reservedAmount);
    }

    private Payment createPayment(PaymentRequest request, Account source, Account target) {
        Payment payment = new Payment();
        payment.setPaymentId(UUID.randomUUID().toString());
        payment.setSourceAccount(source);
        payment.setTargetAccount(target);
        payment.setAmount(request.getAmount());
        payment.setDescription(request.getDescription());
        payment.setCreatedAt(LocalDateTime.now());
        payment.setStatus("COMPLETED");
        return payment;
    }

    private void executeTransfer(Account source, Account target, BigDecimal amount) {
        source.setBalance(source.getBalance().subtract(amount));
        target.setBalance(target.getBalance().add(amount));
        
        accountRepository.save(source);
        accountRepository.save(target);
    }

    private PaymentResponse buildPaymentResponse(Payment payment) {
        PaymentResponse response = new PaymentResponse();
        response.setPaymentId(payment.getPaymentId());
        response.setAmount(payment.getAmount());
        response.setStatus(payment.getStatus());
        response.setTimestamp(payment.getCreatedAt());
        return response;
    }
}