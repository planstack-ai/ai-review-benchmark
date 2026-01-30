package com.example.inventory.service;

import com.example.inventory.entity.Product;
import com.example.inventory.repository.ProductRepository;
import com.example.inventory.dto.StockUpdateRequest;
import com.example.inventory.exception.ProductNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class InventoryService {

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private AuditService auditService;

    public Product createProduct(String name, String sku, BigDecimal price, Integer initialQuantity) {
        Product product = new Product();
        product.setName(name);
        product.setSku(sku);
        product.setPrice(price);
        product.setQuantity(initialQuantity);
        product.setCreatedAt(LocalDateTime.now());
        product.setUpdatedAt(LocalDateTime.now());
        
        Product savedProduct = productRepository.save(product);
        auditService.logProductCreation(savedProduct);
        return savedProduct;
    }

    public Product updateStock(Long productId, Integer quantityChange) {
        Product product = findProductById(productId);
        Integer currentQuantity = product.getQuantity();
        Integer newQuantity = currentQuantity + quantityChange;
        
        product.setQuantity(newQuantity);
        product.setUpdatedAt(LocalDateTime.now());
        
        Product updatedProduct = productRepository.save(product);
        auditService.logStockUpdate(updatedProduct, quantityChange);
        return updatedProduct;
    }

    public Product processStockReduction(Long productId, Integer reductionAmount) {
        if (reductionAmount <= 0) {
            throw new IllegalArgumentException("Reduction amount must be positive");
        }
        
        Product product = findProductById(productId);
        validateProductActive(product);
        
        Integer currentStock = product.getQuantity();
        Integer newStock = calculateNewStock(currentStock, reductionAmount);
        
        return updateProductStock(product, newStock);
    }

    public List<Product> getLowStockProducts(Integer threshold) {
        return productRepository.findByQuantityLessThanEqual(threshold);
    }

    public Product restockProduct(Long productId, Integer additionalQuantity) {
        if (additionalQuantity <= 0) {
            throw new IllegalArgumentException("Additional quantity must be positive");
        }
        
        Product product = findProductById(productId);
        Integer currentQuantity = product.getQuantity();
        Integer newQuantity = currentQuantity + additionalQuantity;
        
        return updateProductStock(product, newQuantity);
    }

    private Product findProductById(Long productId) {
        Optional<Product> productOpt = productRepository.findById(productId);
        if (!productOpt.isPresent()) {
            throw new ProductNotFoundException("Product not found with ID: " + productId);
        }
        return productOpt.get();
    }

    private void validateProductActive(Product product) {
        if (!product.isActive()) {
            throw new IllegalStateException("Cannot modify stock for inactive product");
        }
    }

    private Integer calculateNewStock(Integer currentStock, Integer reductionAmount) {
        return currentStock - reductionAmount;
    }

    private Product updateProductStock(Product product, Integer newQuantity) {
        product.setQuantity(newQuantity);
        product.setUpdatedAt(LocalDateTime.now());
        
        Product updatedProduct = productRepository.save(product);
        auditService.logStockUpdate(updatedProduct, newQuantity - product.getQuantity());
        return updatedProduct;
    }

    public BigDecimal calculateTotalInventoryValue() {
        List<Product> allProducts = productRepository.findAll();
        return allProducts.stream()
                .filter(Product::isActive)
                .map(product -> product.getPrice().multiply(BigDecimal.valueOf(product.getQuantity())))
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}