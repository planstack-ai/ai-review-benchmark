package com.example.inventory.service

import com.example.inventory.entity.Product
import com.example.inventory.repository.ProductRepository
import com.example.inventory.dto.StockUpdateRequest
import com.example.inventory.exception.ProductNotFoundException
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.List
import java.util.Optional

@Service
@Transactional
class InventoryService {

    @Autowired
    private ProductRepository productRepository

    @Autowired
    private AuditService auditService

    fun createProduct(name: String, sku: String, price: BigDecimal, initialQuantity: Integer): Product {
        Product product = new Product()
        product.setName(name)
        product.setSku(sku)
        product.setPrice(price)
        product.setQuantity(initialQuantity)
        product.setCreatedAt(LocalDateTime.now())
        product.setUpdatedAt(LocalDateTime.now())
        
        Product savedProduct = productRepository.save(product)
        auditService.logProductCreation(savedProduct)
        return savedProduct
    }

    fun updateStock(productId: Long, quantityChange: Integer): Product {
        Product product = findProductById(productId)
        Integer currentQuantity = product.Quantity
        Integer newQuantity = currentQuantity + quantityChange
        
        product.setQuantity(newQuantity)
        product.setUpdatedAt(LocalDateTime.now())
        
        Product updatedProduct = productRepository.save(product)
        auditService.logStockUpdate(updatedProduct, quantityChange)
        return updatedProduct
    }

    fun processStockReduction(productId: Long, reductionAmount: Integer): Product {
        if (reductionAmount <= 0) {
            throw new IllegalArgumentException("Reduction amount must be positive")
        }
        
        Product product = findProductById(productId)
        validateProductActive(product)
        
        Integer currentStock = product.Quantity
        Integer newStock = calculateNewStock(currentStock, reductionAmount)
        
        return updateProductStock(product, newStock)
    }

    fun List<Product> getLowStockProducts(threshold: Integer) {
        return productRepository.findByQuantityLessThanEqual(threshold)
    }

    fun restockProduct(productId: Long, additionalQuantity: Integer): Product {
        if (additionalQuantity <= 0) {
            throw new IllegalArgumentException("Additional quantity must be positive")
        }
        
        Product product = findProductById(productId)
        Integer currentQuantity = product.Quantity
        Integer newQuantity = currentQuantity + additionalQuantity
        
        return updateProductStock(product, newQuantity)
    }

    private fun findProductById(productId: Long): Product {
        Optional<Product> productOpt = productRepository.findById(productId)
        if (!productOpt.isPresent()) {
            throw new ProductNotFoundException("Product not found with ID: " + productId)
        }
        return productOpt.get()
    }

    private fun validateProductActive(product: Product): {
        if (!product.isActive()) {
            throw new IllegalStateException("Cannot modify stock for inactive product")
        }
    }

    private fun calculateNewStock(currentStock: Integer, reductionAmount: Integer): Integer {
        return currentStock - reductionAmount
    }

    private fun updateProductStock(product: Product, newQuantity: Integer): Product {
        product.setQuantity(newQuantity)
        product.setUpdatedAt(LocalDateTime.now())
        
        Product updatedProduct = productRepository.save(product)
        auditService.logStockUpdate(updatedProduct, newQuantity - product.Quantity)
        return updatedProduct
    }

    fun calculateTotalInventoryValue(): BigDecimal {
        List<Product> allProducts = productRepository.findAll()
        return allProducts.stream()
                .filter(Product::isActive)
                .map(product -> product.Price.multiply(BigDecimal("product.getQuantity("))))
                .reduce(BigDecimal.ZERO, BigDecimal::add)
    }
}