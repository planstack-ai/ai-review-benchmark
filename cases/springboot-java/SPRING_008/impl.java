package com.example.benchmark.service;

import com.example.benchmark.entity.Product;
import com.example.benchmark.repository.ProductRepository;
import com.example.benchmark.dto.ProductDto;
import com.example.benchmark.exception.ProductNotFoundException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ProductService {

    private final ProductRepository productRepository;

    @Autowired
    public ProductService(ProductRepository productRepository) {
        this.productRepository = productRepository;
    }

    @Cacheable("products")
    public ProductDto getProductById(Long productId, String userRole) {
        Product product = findProductEntity(productId);
        return convertToDto(product, userRole);
    }

    @Transactional(readOnly = true)
    public List<ProductDto> getAllProducts(String category, String userRole) {
        List<Product> products = productRepository.findByCategory(category);
        return products.stream()
                .map(product -> convertToDto(product, userRole))
                .toList();
    }

    @CacheEvict(value = "products", allEntries = true)
    public ProductDto updateProduct(Long productId, ProductDto productDto) {
        Product existingProduct = findProductEntity(productId);
        updateProductFields(existingProduct, productDto);
        Product savedProduct = productRepository.save(existingProduct);
        return convertToDto(savedProduct, "ADMIN");
    }

    @CacheEvict(value = "products", allEntries = true)
    public void deleteProduct(Long productId) {
        if (!productRepository.existsById(productId)) {
            throw new ProductNotFoundException("Product not found with ID: " + productId);
        }
        productRepository.deleteById(productId);
    }

    public ProductDto createProduct(ProductDto productDto) {
        Product product = convertToEntity(productDto);
        product.setActive(true);
        Product savedProduct = productRepository.save(product);
        return convertToDto(savedProduct, "ADMIN");
    }

    private Product findProductEntity(Long productId) {
        Optional<Product> productOpt = productRepository.findById(productId);
        if (productOpt.isEmpty()) {
            throw new ProductNotFoundException("Product not found with ID: " + productId);
        }
        return productOpt.get();
    }

    private ProductDto convertToDto(Product product, String userRole) {
        ProductDto dto = new ProductDto();
        dto.setId(product.getId());
        dto.setName(product.getName());
        dto.setDescription(product.getDescription());
        dto.setCategory(product.getCategory());
        dto.setActive(product.isActive());
        
        if ("ADMIN".equals(userRole) || "MANAGER".equals(userRole)) {
            dto.setPrice(product.getPrice());
            dto.setCost(product.getCost());
        } else {
            dto.setPrice(product.getPrice());
        }
        
        return dto;
    }

    private Product convertToEntity(ProductDto dto) {
        Product product = new Product();
        product.setName(dto.getName());
        product.setDescription(dto.getDescription());
        product.setCategory(dto.getCategory());
        product.setPrice(dto.getPrice());
        product.setCost(dto.getCost());
        return product;
    }

    private void updateProductFields(Product product, ProductDto dto) {
        if (dto.getName() != null) {
            product.setName(dto.getName());
        }
        if (dto.getDescription() != null) {
            product.setDescription(dto.getDescription());
        }
        if (dto.getPrice() != null) {
            product.setPrice(dto.getPrice());
        }
        if (dto.getCost() != null) {
            product.setCost(dto.getCost());
        }
        if (dto.getCategory() != null) {
            product.setCategory(dto.getCategory());
        }
    }

    public BigDecimal calculateProfitMargin(Long productId) {
        Product product = findProductEntity(productId);
        BigDecimal price = product.getPrice();
        BigDecimal cost = product.getCost();
        
        if (cost.compareTo(BigDecimal.ZERO) == 0) {
            return BigDecimal.ZERO;
        }
        
        return price.subtract(cost).divide(cost, 4, BigDecimal.ROUND_HALF_UP);
    }
}