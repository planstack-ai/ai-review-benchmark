package com.example.ecommerce.service;

import com.example.ecommerce.entity.Product;
import com.example.ecommerce.repository.ProductRepository;
import com.example.ecommerce.dto.PriceUpdateRequest;
import com.example.ecommerce.exception.ProductNotFoundException;
import com.example.ecommerce.exception.InvalidPriceException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ProductPriceService {

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private AuditService auditService;

    public Product updateProductPrice(Long productId, PriceUpdateRequest priceRequest) {
        validatePriceRequest(priceRequest);
        
        Product product = findProductById(productId);
        BigDecimal oldPrice = product.getPrice();
        BigDecimal newPrice = priceRequest.getNewPrice();
        
        if (isPriceChangeSignificant(oldPrice, newPrice)) {
            logPriceChange(product, oldPrice, newPrice);
        }
        
        product.setPrice(newPrice);
        product.setLastModified(LocalDateTime.now());
        product.setModifiedBy(getCurrentUsername());
        
        Product savedProduct = productRepository.save(product);
        auditService.logPriceUpdate(productId, oldPrice, newPrice, getCurrentUsername());
        
        return savedProduct;
    }

    public List<Product> updateMultipleProductPrices(List<PriceUpdateRequest> priceRequests) {
        return priceRequests.stream()
                .map(request -> updateProductPrice(request.getProductId(), request))
                .toList();
    }

    public BigDecimal calculateDiscountedPrice(Long productId, BigDecimal discountPercentage) {
        Product product = findProductById(productId);
        BigDecimal currentPrice = product.getPrice();
        BigDecimal discountAmount = currentPrice.multiply(discountPercentage).divide(BigDecimal.valueOf(100));
        return currentPrice.subtract(discountAmount);
    }

    private Product findProductById(Long productId) {
        Optional<Product> productOpt = productRepository.findById(productId);
        if (productOpt.isEmpty()) {
            throw new ProductNotFoundException("Product with ID " + productId + " not found");
        }
        return productOpt.get();
    }

    private void validatePriceRequest(PriceUpdateRequest priceRequest) {
        if (priceRequest.getNewPrice() == null) {
            throw new InvalidPriceException("Price cannot be null");
        }
        if (priceRequest.getNewPrice().compareTo(BigDecimal.ZERO) < 0) {
            throw new InvalidPriceException("Price cannot be negative");
        }
        if (priceRequest.getNewPrice().scale() > 2) {
            throw new InvalidPriceException("Price cannot have more than 2 decimal places");
        }
    }

    private boolean isPriceChangeSignificant(BigDecimal oldPrice, BigDecimal newPrice) {
        BigDecimal changePercentage = newPrice.subtract(oldPrice)
                .divide(oldPrice, 4, BigDecimal.ROUND_HALF_UP)
                .multiply(BigDecimal.valueOf(100))
                .abs();
        return changePercentage.compareTo(BigDecimal.valueOf(10)) > 0;
    }

    private void logPriceChange(Product product, BigDecimal oldPrice, BigDecimal newPrice) {
        String logMessage = String.format("Significant price change for product %s: %s -> %s", 
                product.getName(), oldPrice, newPrice);
        System.out.println(logMessage);
    }

    private String getCurrentUsername() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        return authentication != null ? authentication.getName() : "system";
    }

    @Transactional(readOnly = true)
    public Product getProductWithPrice(Long productId) {
        return findProductById(productId);
    }

    public boolean isValidPriceRange(BigDecimal price, BigDecimal minPrice, BigDecimal maxPrice) {
        return price.compareTo(minPrice) >= 0 && price.compareTo(maxPrice) <= 0;
    }
}