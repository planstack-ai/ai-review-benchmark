package com.example.inventory.service

import com.example.inventory.entity.Product
import com.example.inventory.entity.StockReservation
import com.example.inventory.exception.InsufficientStockException
import com.example.inventory.exception.ProductNotFoundException
import com.example.inventory.repository.ProductRepository
import com.example.inventory.repository.StockReservationRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.*

@Service
@Transactional
class StockReservationService(
    private val productRepository: ProductRepository,
    private val stockReservationRepository: StockReservationRepository
) {

    fun reserveStock(productId: Long, quantity: Int, customerId: String): StockReservation {
        val product = findProductById(productId)
        
        validateReservationRequest(quantity, customerId)
        
        if (isStockAvailable(product, quantity)) {
            updateProductStock(product, quantity)
            return createReservation(product, quantity, customerId)
        } else {
            throw InsufficientStockException("Insufficient stock for product ${product.name}. Available: ${product.stockQuantity}, Requested: $quantity")
        }
    }

    fun cancelReservation(reservationId: String): Boolean {
        val reservation = stockReservationRepository.findByReservationId(reservationId)
            ?: return false

        if (reservation.status == StockReservation.Status.ACTIVE) {
            val product = findProductById(reservation.productId)
            restoreProductStock(product, reservation.quantity)
            
            reservation.status = StockReservation.Status.CANCELLED
            reservation.updatedAt = LocalDateTime.now()
            stockReservationRepository.save(reservation)
            
            return true
        }
        
        return false
    }

    fun confirmReservation(reservationId: String): Boolean {
        val reservation = stockReservationRepository.findByReservationId(reservationId)
            ?: return false

        if (reservation.status == StockReservation.Status.ACTIVE) {
            reservation.status = StockReservation.Status.CONFIRMED
            reservation.updatedAt = LocalDateTime.now()
            stockReservationRepository.save(reservation)
            return true
        }
        
        return false
    }

    private fun findProductById(productId: Long): Product {
        return productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product with ID $productId not found") }
    }

    private fun validateReservationRequest(quantity: Int, customerId: String) {
        require(quantity > 0) { "Quantity must be positive" }
        require(customerId.isNotBlank()) { "Customer ID cannot be blank" }
    }

    private fun isStockAvailable(product: Product, requestedQuantity: Int): Boolean {
        return product.stockQuantity >= requestedQuantity
    }

    private fun updateProductStock(product: Product, quantity: Int) {
        product.stockQuantity = product.stockQuantity - quantity
        product.updatedAt = LocalDateTime.now()
        productRepository.save(product)
    }

    private fun restoreProductStock(product: Product, quantity: Int) {
        product.stockQuantity = product.stockQuantity + quantity
        product.updatedAt = LocalDateTime.now()
        productRepository.save(product)
    }

    private fun createReservation(product: Product, quantity: Int, customerId: String): StockReservation {
        val reservation = StockReservation(
            reservationId = UUID.randomUUID().toString(),
            productId = product.id!!,
            productName = product.name,
            quantity = quantity,
            unitPrice = product.price,
            totalAmount = product.price.multiply(BigDecimal(quantity)),
            customerId = customerId,
            status = StockReservation.Status.ACTIVE,
            createdAt = LocalDateTime.now(),
            updatedAt = LocalDateTime.now()
        )
        
        return stockReservationRepository.save(reservation)
    }

    fun getActiveReservationsByCustomer(customerId: String): List<StockReservation> {
        return stockReservationRepository.findByCustomerIdAndStatus(customerId, StockReservation.Status.ACTIVE)
    }

    fun calculateTotalReservedValue(customerId: String): BigDecimal {
        return getActiveReservationsByCustomer(customerId)
            .sumOf { it.totalAmount }
    }
}