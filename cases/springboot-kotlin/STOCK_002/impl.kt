package com.example.inventory.service

import com.example.inventory.entity.Product
import com.example.inventory.repository.ProductRepository
import com.example.inventory.dto.StockUpdateRequest
import com.example.inventory.dto.StockMovementDto
import com.example.inventory.exception.ProductNotFoundException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
@Transactional
class InventoryService(
    private val productRepository: ProductRepository
) {

    fun updateStock(productId: Long, request: StockUpdateRequest): Product {
        val product = findProductById(productId)
        
        return when (request.operation) {
            "ADD" -> addStock(product, request.quantity)
            "REMOVE" -> removeStock(product, request.quantity)
            "SET" -> setStock(product, request.quantity)
            else -> throw IllegalArgumentException("Invalid operation: ${request.operation}")
        }
    }

    fun processStockMovement(movement: StockMovementDto): Product {
        val product = findProductById(movement.productId)
        
        validateMovementQuantity(movement.quantity)
        
        val updatedProduct = when (movement.type) {
            "SALE" -> processSale(product, movement.quantity)
            "RETURN" -> processReturn(product, movement.quantity)
            "ADJUSTMENT" -> processAdjustment(product, movement.quantity)
            else -> throw IllegalArgumentException("Unknown movement type: ${movement.type}")
        }
        
        logStockMovement(updatedProduct, movement)
        return updatedProduct
    }

    @Transactional(readOnly = true)
    fun getAvailableStock(productId: Long): Int {
        return findProductById(productId).quantity
    }

    private fun addStock(product: Product, quantity: Int): Product {
        product.quantity += quantity
        product.lastUpdated = LocalDateTime.now()
        return productRepository.save(product)
    }

    private fun removeStock(product: Product, quantity: Int): Product {
        product.quantity -= quantity
        product.lastUpdated = LocalDateTime.now()
        return productRepository.save(product)
    }

    private fun setStock(product: Product, quantity: Int): Product {
        product.quantity = quantity
        product.lastUpdated = LocalDateTime.now()
        return productRepository.save(product)
    }

    private fun processSale(product: Product, quantity: Int): Product {
        return removeStock(product, quantity)
    }

    private fun processReturn(product: Product, quantity: Int): Product {
        return addStock(product, quantity)
    }

    private fun processAdjustment(product: Product, quantity: Int): Product {
        return setStock(product, quantity)
    }

    private fun findProductById(productId: Long): Product {
        return productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product not found with id: $productId") }
    }

    private fun validateMovementQuantity(quantity: Int) {
        if (quantity <= 0) {
            throw IllegalArgumentException("Movement quantity must be positive")
        }
    }

    private fun logStockMovement(product: Product, movement: StockMovementDto) {
        println("Stock movement logged: Product ${product.id}, Type: ${movement.type}, Quantity: ${movement.quantity}, New Stock: ${product.quantity}")
    }

    fun calculateStockValue(productId: Long): BigDecimal {
        val product = findProductById(productId)
        return product.price.multiply(BigDecimal.valueOf(product.quantity.toLong()))
    }

    fun isStockSufficient(productId: Long, requiredQuantity: Int): Boolean {
        val availableStock = getAvailableStock(productId)
        return availableStock >= requiredQuantity
    }
}