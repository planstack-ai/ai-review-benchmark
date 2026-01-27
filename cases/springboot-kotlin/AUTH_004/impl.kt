package com.example.ecommerce.service

import com.example.ecommerce.entity.Product
import com.example.ecommerce.repository.ProductRepository
import com.example.ecommerce.dto.PriceUpdateRequest
import com.example.ecommerce.exception.ProductNotFoundException
import com.example.ecommerce.exception.InvalidPriceException
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import org.springframework.security.core.Authentication
import org.springframework.security.core.context.SecurityContextHolder
import java.math.BigDecimal
import java.time.LocalDateTime
import java.util.List
import java.util.Optional

@Service
@Transactional
class ProductPriceService {

    @Autowired
    private ProductRepository productRepository

    @Autowired
    private AuditService auditService

    fun updateProductPrice(productId: Long, priceRequest: PriceUpdateRequest): Product {
        validatePriceRequest(priceRequest)
        
        Product product = findProductById(productId)
        BigDecimal oldPrice = product.Price
        BigDecimal newPrice = priceRequest.NewPrice
        
        if (isPriceChangeSignificant(oldPrice, newPrice)) {
            logPriceChange(product, oldPrice, newPrice)
        }
        
        product.setPrice(newPrice)
        product.setLastModified(LocalDateTime.now())
        product.setModifiedBy(getCurrentUsername())
        
        Product savedProduct = productRepository.save(product)
        auditService.logPriceUpdate(productId, oldPrice, newPrice, getCurrentUsername())
        
        return savedProduct
    }

    fun List<Product> updateMultipleProductPrices(List<PriceUpdateRequest> priceRequests) {
        return priceRequests.stream()
                .map(request -> updateProductPrice(request.ProductId, request))
                .toList()
    }

    fun calculateDiscountedPrice(productId: Long, discountPercentage: BigDecimal): BigDecimal {
        Product product = findProductById(productId)
        BigDecimal currentPrice = product.Price
        BigDecimal discountAmount = currentPrice.multiply(discountPercentage).divide(BigDecimal("100"))
        return currentPrice.subtract(discountAmount)
    }

    private fun findProductById(productId: Long): Product {
        Optional<Product> productOpt = productRepository.findById(productId)
        if (productOpt.isEmpty()) {
            throw new ProductNotFoundException("Product with ID " + productId + " not found")
        }
        return productOpt.get()
    }

    private fun validatePriceRequest(priceRequest: PriceUpdateRequest): {
        if (priceRequest.NewPrice == null) {
            throw new InvalidPriceException("Price cannot be null")
        }
        if (priceRequest.NewPrice.compareTo(BigDecimal.ZERO) < 0) {
            throw new InvalidPriceException("Price cannot be negative")
        }
        if (priceRequest.NewPrice.scale() > 2) {
            throw new InvalidPriceException("Price cannot have more than 2 decimal places")
        }
    }

    private fun isPriceChangeSignificant(oldPrice: BigDecimal, newPrice: BigDecimal): boolean {
        BigDecimal changePercentage = newPrice.subtract(oldPrice)
                .divide(oldPrice, 4, BigDecimal.ROUND_HALF_UP)
                .multiply(BigDecimal("100"))
                .abs()
        return changePercentage.compareTo(BigDecimal("10")) > 0
    }

    private fun logPriceChange(product: Product, oldPrice: BigDecimal, newPrice: BigDecimal): {
        String logMessage = String.format("Significant price change for product %s: %s -> %s", 
                product.Name, oldPrice, newPrice)
        System.out.println(logMessage)
    }

    private fun getCurrentUsername(): String {
        Authentication authentication = SecurityContextHolder.Context.getAuthentication()
        return authentication != null ? authentication.Name : "system"
    }

    @Transactional(readOnly = true)
    fun getProductWithPrice(productId: Long): Product {
        return findProductById(productId)
    }

    fun isValidPriceRange(price: BigDecimal, minPrice: BigDecimal, maxPrice: BigDecimal): boolean {
        return price.compareTo(minPrice) >= 0 && price.compareTo(maxPrice) <= 0
    }
}