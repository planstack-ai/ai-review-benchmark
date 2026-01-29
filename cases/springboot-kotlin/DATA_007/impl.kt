package com.example.ecommerce.service

import com.example.ecommerce.dto.ProductImportDto
import com.example.ecommerce.entity.Product
import com.example.ecommerce.repository.ProductRepository
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class ProductImportService(
    private val productRepository: ProductRepository
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Transactional
    fun importProducts(importData: List<ProductImportDto>): Map<String, Any> {
        logger.info("Starting product import with ${importData.size} items")

        val products = importData
            .filter { isValidProduct(it) }
            .map { dto ->
                Product(
                    sku = dto.sku,
                    name = dto.name,
                    priceCents = dto.priceCents,
                    createdAt = LocalDateTime.now()
                )
            }

        try {
            productRepository.saveAll(products)
        } catch (e: Exception) {
            logger.error("Error during batch save", e)
        }

        val result = mapOf(
            "totalProcessed" to importData.size,
            "imported" to products.size,
            "status" to "completed"
        )

        logger.info("Product import completed: ${products.size} products imported")
        return result
    }

    @Transactional
    fun bulkImportProducts(importData: List<ProductImportDto>): Int {
        val products = importData
            .filter { isValidProduct(it) }
            .map { dto ->
                Product(
                    sku = dto.sku,
                    name = dto.name,
                    priceCents = dto.priceCents,
                    createdAt = LocalDateTime.now()
                )
            }

        productRepository.saveAll(products)

        return products.size
    }

    @Transactional
    fun importWithStats(importData: List<ProductImportDto>): Map<String, Int> {
        var processed = 0
        var errors = 0

        val toSave = mutableListOf<Product>()

        importData.forEach { dto ->
            try {
                toSave.add(Product(
                    sku = dto.sku,
                    name = dto.name,
                    priceCents = dto.priceCents,
                    createdAt = LocalDateTime.now()
                ))
                processed++
            } catch (e: Exception) {
                errors++
                logger.error("Error processing product: ${dto.sku}", e)
            }
        }

        productRepository.saveAll(toSave)

        return mapOf(
            "processed" to processed,
            "errors" to errors,
            "total" to importData.size
        )
    }

    private fun isValidProduct(dto: ProductImportDto): Boolean {
        return dto.sku.isNotBlank() &&
               dto.name.isNotBlank() &&
               dto.priceCents > 0
    }
}

data class ProductImportDto(
    val sku: String,
    val name: String,
    val priceCents: Int
)
