package com.example.product.service

import com.example.product.entity.Product
import com.example.product.repository.ProductRepository
import org.springframework.cache.annotation.CacheEvict
import org.springframework.cache.annotation.Cacheable
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

@Service
class ProductService(
    private val productRepository: ProductRepository
) {

    @Cacheable("products")
    fun getProductById(productId: Long): Product {
        return productRepository.findById(productId)
            .orElseThrow { IllegalArgumentException("Product not found: $productId") }
    }

    @Cacheable("products")
    fun getProductDetails(productId: Long, includeInactive: Boolean = false): Product {
        val product = productRepository.findById(productId)
            .orElseThrow { IllegalArgumentException("Product not found: $productId") }

        if (!includeInactive && !product.isActive) {
            throw IllegalArgumentException("Product is not active: $productId")
        }

        return product
    }

    fun getProductsByCategory(category: String): List<Product> {
        return productRepository.findByCategory(category)
            .filter { it.isActive }
    }

    fun getActiveProducts(): List<Product> {
        return productRepository.findByIsActive(true)
    }

    @Transactional
    @CacheEvict(value = ["products"], allEntries = true)
    fun updateProductPrice(productId: Long, newPrice: BigDecimal): Product {
        val product = productRepository.findById(productId)
            .orElseThrow { IllegalArgumentException("Product not found: $productId") }

        if (newPrice <= BigDecimal.ZERO) {
            throw IllegalArgumentException("Price must be positive")
        }

        val updatedProduct = product.copy(price = newPrice)
        return productRepository.save(updatedProduct)
    }

    @Transactional
    @CacheEvict(value = ["products"], allEntries = true)
    fun updateStockQuantity(productId: Long, quantity: Int): Product {
        val product = productRepository.findById(productId)
            .orElseThrow { IllegalArgumentException("Product not found: $productId") }

        if (quantity < 0) {
            throw IllegalArgumentException("Stock quantity cannot be negative")
        }

        product.stockQuantity = quantity
        return productRepository.save(product)
    }

    @Transactional
    @CacheEvict(value = ["products"], allEntries = true)
    fun deactivateProduct(productId: Long) {
        val product = productRepository.findById(productId)
            .orElseThrow { IllegalArgumentException("Product not found: $productId") }

        product.isActive = false
        productRepository.save(product)
    }

    fun checkProductAvailability(productId: Long): Boolean {
        val product = getProductById(productId)
        return product.isActive && product.stockQuantity > 0
    }
}
