package com.example.benchmark.service

import com.example.benchmark.dto.PaymentRequest
import com.example.benchmark.dto.PaymentResponse
import com.example.benchmark.entity.Payment
import com.example.benchmark.entity.Account
import com.example.benchmark.repository.PaymentRepository
import com.example.benchmark.repository.AccountRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.http.ResponseEntity
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.Optional
import java.util.UUID

@Service
@Transactional
class PaymentProcessingService {

    @Autowired
    private PaymentRepository paymentRepository

    @Autowired
    private AccountRepository accountRepository

    @Autowired
    private NotificationService notificationService

    fun ResponseEntity<?> processPayment(request: PaymentRequest) {
        try {
            validatePaymentRequest(request)
            
            Account sourceAccount = getAccountById(request.SourceAccountId)
            Account targetAccount = getAccountById(request.TargetAccountId)
            
            BigDecimal amount = request.Amount
            
            if (hasInsufficientFunds(sourceAccount, amount)) {
                return ResponseEntity.badRequest().body("Insufficient funds available")
            }
            
            Payment payment = createPayment(request, sourceAccount, targetAccount)
            executeTransfer(sourceAccount, targetAccount, amount)
            
            Payment savedPayment = paymentRepository.save(payment)
            notificationService.sendPaymentConfirmation(savedPayment)
            
            PaymentResponse response = buildPaymentResponse(savedPayment)
            return ResponseEntity.ok(response)
            
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(e.Message)
        }
    }

    private fun validatePaymentRequest(request: PaymentRequest): {
        if (request.Amount == null || request.Amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Payment amount must be positive")
        }
        
        if (request.SourceAccountId == null || request.TargetAccountId == null) {
            throw new IllegalArgumentException("Source and target account IDs are required")
        }
        
        if (request.SourceAccountId.equals(request.TargetAccountId)) {
            throw new IllegalArgumentException("Source and target accounts cannot be the same")
        }
    }

    private fun getAccountById(accountId: Long): Account {
        Optional<Account> account = accountRepository.findById(accountId)
        if (!account.isPresent()) {
            throw new RuntimeException("Account not found with ID: " + accountId)
        }
        
        if (!account.get().isActive()) {
            throw new RuntimeException("Account is inactive: " + accountId)
        }
        
        return account.get()
    }

    private fun hasInsufficientFunds(account: Account, amount: BigDecimal): boolean {
        BigDecimal availableBalance = calculateAvailableBalance(account)
        return availableBalance.compareTo(amount) < 0
    }

    private fun calculateAvailableBalance(account: Account): BigDecimal {
        BigDecimal currentBalance = account.Balance
        BigDecimal reservedAmount = account.ReservedAmount
        return currentBalance.subtract(reservedAmount)
    }

    private fun createPayment(request: PaymentRequest, source: Account, target: Account): Payment {
        Payment payment = new Payment()
        payment.setPaymentId(UUID.randomUUID().toString())
        payment.setSourceAccount(source)
        payment.setTargetAccount(target)
        payment.setAmount(request.Amount)
        payment.setDescription(request.Description)
        payment.setCreatedAt(LocalDateTime.now())
        payment.setStatus("COMPLETED")
        return payment
    }

    private fun executeTransfer(source: Account, target: Account, amount: BigDecimal): {
        source.setBalance(source.Balance.subtract(amount))
        target.setBalance(target.Balance.add(amount))
        
        accountRepository.save(source)
        accountRepository.save(target)
    }

    private fun buildPaymentResponse(payment: Payment): PaymentResponse {
        PaymentResponse response = new PaymentResponse()
        response.setPaymentId(payment.PaymentId)
        response.setAmount(payment.Amount)
        response.setStatus(payment.Status)
        response.setTimestamp(payment.CreatedAt)
        return response
    }
}