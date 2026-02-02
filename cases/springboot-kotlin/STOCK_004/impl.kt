package com.example.inventory.service

import com.example.inventory.entity.Product
import com.example.inventory.entity.StockReservation
import com.example.inventory.entity.ReservationStatus
import com.example.inventory.entity.InventorySnapshot
import com.example.inventory.repository.ProductRepository
import com.example.inventory.repository.StockReservationRepository
import com.example.inventory.repository.InventorySnapshotRepository
import com.example.inventory.exception.InsufficientStockException
import com.example.inventory.exception.ProductNotFoundException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime
import java.math.BigDecimal

@Service
@Transactional
class StockAvailabilityService(
    private val productRepository: ProductRepository,
    private val stockReservationRepository: StockReservationRepository,
    private val inventorySnapshotRepository: InventorySnapshotRepository
) {

    fun checkAvailability(productId: Long): StockAvailabilityInfo {
        val product = productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product not found: $productId") }

        val availableStock = calculateAvailableStock(product)

        return StockAvailabilityInfo(
            productId = product.id,
            productName = product.name,
            totalStock = product.totalStock,
            reservedStock = product.reservedStock,
            availableStock = availableStock,
            isAvailable = availableStock > 0,
            lastCheckedAt = LocalDateTime.now()
        )
    }

    fun checkAvailabilityForQuantity(productId: Long, requestedQuantity: Int): Boolean {
        val product = productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product not found: $productId") }

        val availableStock = calculateAvailableStock(product)
        return availableStock >= requestedQuantity
    }

    fun getBulkAvailability(productIds: List<Long>): List<StockAvailabilityInfo> {
        val products = productRepository.findByIdIn(productIds)

        return products.map { product ->
            StockAvailabilityInfo(
                productId = product.id,
                productName = product.name,
                totalStock = product.totalStock,
                reservedStock = product.reservedStock,
                availableStock = calculateAvailableStock(product),
                isAvailable = calculateAvailableStock(product) > 0,
                lastCheckedAt = LocalDateTime.now()
            )
        }
    }

    fun reserveStock(productId: Long, quantity: Int, customerId: Long): ReservationResult {
        val product = productRepository.findByIdWithLock(productId)
            ?: throw ProductNotFoundException("Product not found: $productId")

        val availableStock = calculateAvailableStock(product)

        if (availableStock < quantity) {
            throw InsufficientStockException(
                "Insufficient stock for product $productId. Available: $availableStock, Requested: $quantity"
            )
        }

        product.reservedStock += quantity
        productRepository.save(product)

        val reservation = StockReservation(
            productId = productId,
            quantity = quantity,
            status = ReservationStatus.ACTIVE,
            expiresAt = LocalDateTime.now().plusMinutes(15)
        )

        val savedReservation = stockReservationRepository.save(reservation)

        return ReservationResult(
            reservationId = savedReservation.id,
            productId = productId,
            quantity = quantity,
            expiresAt = savedReservation.expiresAt,
            success = true
        )
    }

    fun releaseReservation(reservationId: Long) {
        val reservation = stockReservationRepository.findById(reservationId)
            .orElseThrow { IllegalArgumentException("Reservation not found: $reservationId") }

        if (reservation.status != ReservationStatus.ACTIVE) {
            return
        }

        val product = productRepository.findByIdWithLock(reservation.productId)
            ?: throw ProductNotFoundException("Product not found: ${reservation.productId}")

        product.reservedStock = maxOf(0, product.reservedStock - reservation.quantity)
        productRepository.save(product)

        reservation.status = ReservationStatus.CANCELLED
        stockReservationRepository.save(reservation)
    }

    fun confirmReservation(reservationId: Long) {
        val reservation = stockReservationRepository.findById(reservationId)
            .orElseThrow { IllegalArgumentException("Reservation not found: $reservationId") }

        if (reservation.status != ReservationStatus.ACTIVE) {
            throw IllegalStateException("Reservation is not active: $reservationId")
        }

        val product = productRepository.findByIdWithLock(reservation.productId)
            ?: throw ProductNotFoundException("Product not found: ${reservation.productId}")

        product.totalStock -= reservation.quantity
        product.reservedStock -= reservation.quantity
        productRepository.save(product)

        reservation.status = ReservationStatus.CONFIRMED
        stockReservationRepository.save(reservation)
    }

    private fun calculateAvailableStock(product: Product): Int {
        return product.totalStock
    }

    fun createInventorySnapshot(productId: Long) {
        val product = productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product not found: $productId") }

        val availableStock = calculateAvailableStock(product)

        val snapshot = InventorySnapshot(
            productId = product.id,
            totalStock = product.totalStock,
            reservedStock = product.reservedStock,
            availableStock = availableStock
        )

        inventorySnapshotRepository.save(snapshot)
    }

    fun getInventoryHistory(productId: Long): List<InventorySnapshot> {
        return inventorySnapshotRepository.findByProductIdOrderBySnapshotAtDesc(productId)
    }
}

data class StockAvailabilityInfo(
    val productId: Long,
    val productName: String,
    val totalStock: Int,
    val reservedStock: Int,
    val availableStock: Int,
    val isAvailable: Boolean,
    val lastCheckedAt: LocalDateTime
)

data class ReservationResult(
    val reservationId: Long,
    val productId: Long,
    val quantity: Int,
    val expiresAt: LocalDateTime,
    val success: Boolean,
    val message: String? = null
)
