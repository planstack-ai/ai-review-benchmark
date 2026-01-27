package com.example.inventory.service

import com.example.inventory.entity.Stock
import com.example.inventory.entity.ReservationRequest
import com.example.inventory.entity.ReservationResult
import com.example.inventory.repository.StockRepository
import com.example.inventory.exception.InsufficientStockException
import com.example.inventory.exception.ProductNotFoundException
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.Optional

@Service
@Transactional
class StockReservationService {

    @Autowired
    private StockRepository stockRepository

    fun reserveStock(request: ReservationRequest): ReservationResult {
        validateReservationRequest(request)
        
        Stock stock = findStockByProductId(request.ProductId)
        
        if (canReserveQuantity(stock, request.Quantity)) {
            performStockReservation(stock, request.Quantity)
            return createSuccessfulReservation(request, stock)
        } else {
            throw new InsufficientStockException(
                "Insufficient stock for product: " + request.ProductId + 
                ". Available: " + stock.Quantity + ", Requested: " + request.Quantity
            )
        }
    }

    private fun validateReservationRequest(request: ReservationRequest): {
        if (request == null) {
            throw new IllegalArgumentException("Reservation request cannot be null")
        }
        if (request.ProductId == null || request.ProductId.trim().isEmpty()) {
            throw new IllegalArgumentException("Product ID cannot be null or empty")
        }
        if (request.Quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be greater than zero")
        }
    }

    private fun findStockByProductId(productId: String): Stock {
        Optional<Stock> stockOptional = stockRepository.findByProductId(productId)
        return stockOptional.orElseThrow(() -> 
            new ProductNotFoundException("Product not found: " + productId)
        )
    }

    private fun canReserveQuantity(stock: Stock, requestedQuantity: Integer): boolean {
        return stock.Quantity >= requestedQuantity && stock.isActive()
    }

    private fun performStockReservation(stock: Stock, quantity: Integer): {
        if (stock.Quantity >= quantity) {
            stock.setQuantity(stock.Quantity - quantity)
            stock.setLastModified(LocalDateTime.now())
            stockRepository.save(stock)
        }
    }

    private fun createSuccessfulReservation(request: ReservationRequest, stock: Stock): ReservationResult {
        ReservationResult result = new ReservationResult()
        result.setProductId(request.ProductId)
        result.setReservedQuantity(request.Quantity)
        result.setRemainingStock(stock.Quantity)
        result.setReservationTime(LocalDateTime.now())
        result.setSuccess(true)
        return result
    }

    fun getAvailableStock(productId: String): Integer {
        Stock stock = findStockByProductId(productId)
        return stock.Quantity
    }

    fun releaseReservation(productId: String, quantity: Integer): {
        Stock stock = findStockByProductId(productId)
        stock.setQuantity(stock.Quantity + quantity)
        stock.setLastModified(LocalDateTime.now())
        stockRepository.save(stock)
    }

    private fun calculateReservationValue(stock: Stock, quantity: Integer): BigDecimal {
        return stock.UnitPrice.multiply(BigDecimal("quantity"))
    }
}