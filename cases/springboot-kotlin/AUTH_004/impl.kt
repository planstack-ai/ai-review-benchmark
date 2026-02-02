package com.example.ecommerce.service

import com.example.ecommerce.entity.Product
import com.example.ecommerce.entity.PriceHistory
import com.example.ecommerce.repository.ProductRepository
import com.example.ecommerce.repository.PriceHistoryRepository
import com.example.ecommerce.dto.PriceUpdateRequest
import com.example.ecommerce.exception.ProductNotFoundException
import com.example.ecommerce.exception.InvalidPriceException
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.security.core.context.SecurityContextHolder
import java.math.BigDecimal
import java.time.LocalDateTime

@Service
@Transactional
class ProductPriceService(
    private val productRepository: ProductRepository,
    private val priceHistoryRepository: PriceHistoryRepository
) {

    fun updateProductPrice(productId: Long, priceUpdateRequest: PriceUpdateRequest): Product {
        val product = findProductById(productId)
        val newPrice = priceUpdateRequest.newPrice
        
        validatePriceUpdate(product, newPrice)
        
        val oldPrice = product.price
        product.price = newPrice
        product.lastModified = LocalDateTime.now()
        product.modifiedBy = getCurrentUsername()
        
        val updatedProduct = productRepository.save(product)
        recordPriceHistory(product, oldPrice, newPrice)
        
        return updatedProduct
    }

    fun bulkUpdatePrices(priceUpdates: List<PriceUpdateRequest>): List<Product> {
        return priceUpdates.map { request ->
            updateProductPrice(request.productId, request)
        }
    }

    fun getPriceHistory(productId: Long): List<PriceHistory> {
        val product = findProductById(productId)
        return priceHistoryRepository.findByProductIdOrderByChangedAtDesc(productId)
    }

    fun applyDiscountToCategory(categoryId: Long, discountPercentage: BigDecimal): List<Product> {
        val products = productRepository.findByCategoryId(categoryId)
        
        return products.map { product ->
            val discountedPrice = calculateDiscountedPrice(product.price, discountPercentage)
            val priceUpdateRequest = PriceUpdateRequest(
                productId = product.id!!,
                newPrice = discountedPrice,
                reason = "Category discount applied: ${discountPercentage}%"
            )
            updateProductPrice(product.id!!, priceUpdateRequest)
        }
    }

    private fun findProductById(productId: Long): Product {
        return productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product with ID $productId not found") }
    }

    private fun validatePriceUpdate(product: Product, newPrice: BigDecimal) {
        when {
            newPrice <= BigDecimal.ZERO -> 
                throw InvalidPriceException("Price must be greater than zero")
            newPrice > BigDecimal("999999.99") -> 
                throw InvalidPriceException("Price cannot exceed 999,999.99")
            newPrice == product.price -> 
                throw InvalidPriceException("New price must be different from current price")
        }
    }

    private fun calculateDiscountedPrice(originalPrice: BigDecimal, discountPercentage: BigDecimal): BigDecimal {
        val discountAmount = originalPrice.multiply(discountPercentage).divide(BigDecimal("100"))
        return originalPrice.subtract(discountAmount).setScale(2, BigDecimal.ROUND_HALF_UP)
    }

    private fun recordPriceHistory(product: Product, oldPrice: BigDecimal, newPrice: BigDecimal) {
        val priceHistory = PriceHistory(
            productId = product.id!!,
            oldPrice = oldPrice,
            newPrice = newPrice,
            changedBy = getCurrentUsername(),
            changedAt = LocalDateTime.now(),
            reason = "Price updated via admin interface"
        )
        priceHistoryRepository.save(priceHistory)
    }

    private fun getCurrentUsername(): String {
        return SecurityContextHolder.getContext().authentication?.name ?: "system"
    }

    @Transactional(readOnly = true)
    fun validatePriceChangePermissions(userId: Long): Boolean {
        return productRepository.existsById(userId)
    }
}