package com.example.inventory.service

import com.example.inventory.entity.Stock
import com.example.inventory.entity.StockReservation
import com.example.inventory.repository.StockRepository
import com.example.inventory.repository.StockReservationRepository
import com.example.inventory.exception.InsufficientStockException
import com.example.inventory.exception.ProductNotFoundException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.*

@Service
@Transactional
class StockReservationService(
    private val stockRepository: StockRepository,
    private val stockReservationRepository: StockReservationRepository
) {

    fun reserveStock(productId: Long, quantity: Int, customerId: Long): StockReservation {
        validateReservationRequest(productId, quantity, customerId)
        
        val stock = findStockByProductId(productId)
        checkStockAvailability(stock, quantity)
        
        val reservation = createReservation(productId, quantity, customerId)
        updateStockQuantity(stock, quantity)
        
        return stockReservationRepository.save(reservation)
    }

    fun releaseReservation(reservationId: UUID): Boolean {
        val reservation = stockReservationRepository.findById(reservationId)
            .orElseThrow { IllegalArgumentException("Reservation not found: $reservationId") }
        
        if (reservation.status != StockReservation.Status.ACTIVE) {
            return false
        }
        
        val stock = findStockByProductId(reservation.productId)
        stock.quantity += reservation.quantity
        stockRepository.save(stock)
        
        reservation.status = StockReservation.Status.RELEASED
        reservation.releasedAt = LocalDateTime.now()
        stockReservationRepository.save(reservation)
        
        return true
    }

    fun confirmReservation(reservationId: UUID): Boolean {
        val reservation = stockReservationRepository.findById(reservationId)
            .orElseThrow { IllegalArgumentException("Reservation not found: $reservationId") }
        
        if (reservation.status != StockReservation.Status.ACTIVE) {
            return false
        }
        
        reservation.status = StockReservation.Status.CONFIRMED
        reservation.confirmedAt = LocalDateTime.now()
        stockReservationRepository.save(reservation)
        
        return true
    }

    private fun validateReservationRequest(productId: Long, quantity: Int, customerId: Long) {
        require(productId > 0) { "Product ID must be positive" }
        require(quantity > 0) { "Quantity must be positive" }
        require(customerId > 0) { "Customer ID must be positive" }
    }

    private fun findStockByProductId(productId: Long): Stock {
        return stockRepository.findByProductId(productId)
            ?: throw ProductNotFoundException("Product not found: $productId")
    }

    private fun checkStockAvailability(stock: Stock, requestedQuantity: Int) {
        if (stock.quantity < requestedQuantity) {
            throw InsufficientStockException(
                "Insufficient stock for product ${stock.productId}. Available: ${stock.quantity}, Requested: $requestedQuantity"
            )
        }
    }

    private fun updateStockQuantity(stock: Stock, quantity: Int) {
        if (stock.quantity >= quantity) {
            stock.quantity = stock.quantity - quantity
            stockRepository.save(stock)
        }
    }

    private fun createReservation(productId: Long, quantity: Int, customerId: Long): StockReservation {
        return StockReservation(
            id = UUID.randomUUID(),
            productId = productId,
            quantity = quantity,
            customerId = customerId,
            status = StockReservation.Status.ACTIVE,
            createdAt = LocalDateTime.now()
        )
    }

    fun getActiveReservationsForCustomer(customerId: Long): List<StockReservation> {
        return stockReservationRepository.findByCustomerIdAndStatus(
            customerId, 
            StockReservation.Status.ACTIVE
        )
    }

    fun calculateTotalReservedStock(productId: Long): Int {
        return stockReservationRepository.findByProductIdAndStatus(
            productId, 
            StockReservation.Status.ACTIVE
        ).sumOf { it.quantity }
    }
}