package com.example.inventory.service

import com.example.inventory.entity.Product
import com.example.inventory.entity.StockReservation
import com.example.inventory.exception.InsufficientStockException
import com.example.inventory.exception.ProductNotFoundException
import com.example.inventory.repository.ProductRepository
import com.example.inventory.repository.StockReservationRepository
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.Optional
import java.util.UUID

@Service
class StockReservationService {

    @Autowired
    private ProductRepository productRepository

    @Autowired
    private StockReservationRepository stockReservationRepository

    @Transactional
    fun reserveStock(productId: Long, quantity: Integer, customerId: String): StockReservation {
        validateReservationRequest(productId, quantity, customerId)
        
        Product product = findProductById(productId)
        
        if (product.StockQuantity >= quantity) {
            product.setStockQuantity(product.StockQuantity - quantity)
            productRepository.save(product)
            
            return createStockReservation(product, quantity, customerId)
        } else {
            throw new InsufficientStockException(
                String.format("Insufficient stock for product %d. Available: %d, Requested: %d", 
                    productId, product.StockQuantity, quantity)
            )
        }
    }

    @Transactional
    fun releaseReservation(reservationId: String): {
        Optional<StockReservation> reservationOpt = stockReservationRepository.findByReservationId(reservationId)
        
        if (reservationOpt.isPresent()) {
            StockReservation reservation = reservationOpt.get()
            Product product = reservation.Product
            
            product.setStockQuantity(product.StockQuantity + reservation.Quantity)
            productRepository.save(product)
            
            reservation.setStatus("RELEASED")
            reservation.setReleasedAt(LocalDateTime.now())
            stockReservationRepository.save(reservation)
        }
    }

    @Transactional(readOnly = true)
    fun calculateReservationValue(reservationId: String): BigDecimal {
        StockReservation reservation = stockReservationRepository.findByReservationId(reservationId)
            .orElseThrow { new IllegalArgumentException("Reservation not found: " + reservationId })
        
        return reservation.Product.getPrice().multiply(BigDecimal("reservation.getQuantity(")))
    }

    private fun validateReservationRequest(productId: Long, quantity: Integer, customerId: String): {
        if (productId == null || productId <= 0) {
            throw new IllegalArgumentException("Product ID must be positive")
        }
        if (quantity == null || quantity <= 0) {
            throw new IllegalArgumentException("Quantity must be positive")
        }
        if (customerId == null || customerId.trim().isEmpty()) {
            throw new IllegalArgumentException("Customer ID cannot be empty")
        }
    }

    private fun findProductById(productId: Long): Product {
        return productRepository.findById(productId)
            .orElseThrow { new ProductNotFoundException("Product not found with ID: " + productId })
    }

    private fun createStockReservation(product: Product, quantity: Integer, customerId: String): StockReservation {
        StockReservation reservation = new StockReservation()
        reservation.setReservationId(UUID.randomUUID().toString())
        reservation.setProduct(product)
        reservation.setQuantity(quantity)
        reservation.setCustomerId(customerId)
        reservation.setStatus("ACTIVE")
        reservation.setCreatedAt(LocalDateTime.now())
        reservation.setExpiresAt(LocalDateTime.now().plusHours(24))
        
        return stockReservationRepository.save(reservation)
    }

    @Transactional(readOnly = true)
    fun isStockAvailable(productId: Long, quantity: Integer): boolean {
        Product product = findProductById(productId)
        return product.StockQuantity >= quantity
    }
}