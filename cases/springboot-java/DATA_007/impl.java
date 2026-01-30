package com.example.ecommerce.service;

import com.example.ecommerce.dto.ProductImportDto;
import com.example.ecommerce.entity.Product;
import com.example.ecommerce.repository.ProductRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class ProductImportService {

    private static final Logger logger = LoggerFactory.getLogger(ProductImportService.class);

    @Autowired
    private ProductRepository productRepository;

    @Transactional
    public Map<String, Object> importProducts(List<ProductImportDto> importData) {
        logger.info("Starting product import with {} items", importData.size());

        List<Product> products = new ArrayList<>();

        for (ProductImportDto dto : importData) {
            if (!isValidProduct(dto)) {
                logger.warn("Skipping invalid product: {}", dto.getSku());
                continue;
            }

            Product product = new Product();
            product.setSku(dto.getSku());
            product.setName(dto.getName());
            product.setPriceCents(dto.getPriceCents());
            product.setCreatedAt(LocalDateTime.now());
            products.add(product);
        }

        try {
            productRepository.saveAll(products);
        } catch (Exception e) {
            logger.error("Error during batch save", e);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("totalProcessed", importData.size());
        result.put("imported", products.size());
        result.put("status", "completed");

        logger.info("Product import completed: {} products imported", products.size());
        return result;
    }

    @Transactional
    public int bulkImportProducts(List<ProductImportDto> importData) {
        List<Product> products = importData.stream()
                .filter(this::isValidProduct)
                .map(dto -> {
                    Product product = new Product();
                    product.setSku(dto.getSku());
                    product.setName(dto.getName());
                    product.setPriceCents(dto.getPriceCents());
                    product.setCreatedAt(LocalDateTime.now());
                    return product;
                })
                .toList();

        productRepository.saveAll(products);

        return products.size();
    }

    @Transactional
    public Map<String, Integer> importWithStats(List<ProductImportDto> importData) {
        int processed = 0;
        int errors = 0;

        List<Product> toSave = new ArrayList<>();

        for (ProductImportDto dto : importData) {
            try {
                Product product = new Product();
                product.setSku(dto.getSku());
                product.setName(dto.getName());
                product.setPriceCents(dto.getPriceCents());
                product.setCreatedAt(LocalDateTime.now());
                toSave.add(product);
                processed++;
            } catch (Exception e) {
                errors++;
                logger.error("Error processing product: {}", dto.getSku(), e);
            }
        }

        productRepository.saveAll(toSave);

        Map<String, Integer> stats = new HashMap<>();
        stats.put("processed", processed);
        stats.put("errors", errors);
        stats.put("total", importData.size());

        return stats;
    }

    private boolean isValidProduct(ProductImportDto dto) {
        return dto != null &&
               dto.getSku() != null && !dto.getSku().isEmpty() &&
               dto.getName() != null && !dto.getName().isEmpty() &&
               dto.getPriceCents() != null && dto.getPriceCents() > 0;
    }
}
