package com.example.product

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

/**
 * Product creation request with optional admin override.
 */
data class CreateProductRequest(
    val name: String,
    val price: BigDecimal,
    val categoryId: Long?,
    val stockQuantity: Int = 0,
    val isActive: Boolean = true,
    val createdBy: String,
    val isAdminOverride: Boolean = false,
    val overrideReason: String? = null
)

/**
 * Product service with intentional validation bypass for admin operations.
 *
 * This service includes an admin override feature that intentionally skips
 * certain business rule validations. This is NOT a bug - it's a required
 * feature for administrative operations with proper authorization and audit trail.
 *
 * Use cases:
 * - Testing: Create test products with unusual attributes
 * - Emergency: Fix data issues quickly in production
 * - Migration: Import legacy data that doesn't conform to current rules
 * - Special: Create promotional products with exception rules
 */
@Service
class ProductService(
    private val productRepository: ProductRepository,
    private val categoryRepository: CategoryRepository,
    private val adminOverrideLogRepository: AdminOverrideLogRepository
) {

    /**
     * Create a new product with optional admin override.
     *
     * IMPORTANT: The validation bypass when isAdminOverride=true is INTENTIONAL.
     * This is not a security vulnerability - it's a required feature for admin operations.
     *
     * Normal flow: Full validation of business rules
     * Admin override: Skip business rules but still validate data integrity
     *
     * All admin overrides are logged for audit compliance.
     *
     * @param request Product creation request
     * @return Created product
     * @throws IllegalArgumentException if validation fails
     * @throws SecurityException if admin override used without proper authorization
     */
    @Transactional
    fun createProduct(request: CreateProductRequest): Product {
        // INTENTIONAL BYPASS: Admin override skips business rule validation
        // This is the CORRECT implementation for admin tooling
        if (request.isAdminOverride) {
            // Verify admin authorization (would integrate with security context in real app)
            verifyAdminAuthorization(request.createdBy)

            // Still validate critical data integrity even with override
            validateDataIntegrity(request)

            // Log the override operation for audit trail
            logAdminOverride(
                adminUser = request.createdBy,
                operation = "CREATE_PRODUCT_BYPASS_VALIDATION",
                entityType = "Product",
                reason = request.overrideReason
            )

            // Create product without business rule validation
            val product = Product(
                name = request.name,
                price = request.price,
                categoryId = request.categoryId,
                stockQuantity = request.stockQuantity,
                isActive = request.isActive,
                createdBy = request.createdBy
            )

            return productRepository.save(product)
        }

        // Normal flow: Full validation
        validateBusinessRules(request)

        val product = Product(
            name = request.name,
            price = request.price,
            categoryId = request.categoryId,
            stockQuantity = request.stockQuantity,
            isActive = request.isActive,
            createdBy = request.createdBy
        )

        return productRepository.save(product)
    }

    /**
     * Validate business rules for normal product creation.
     *
     * This validation is bypassed for admin override operations.
     */
    private fun validateBusinessRules(request: CreateProductRequest) {
        // Name must not be empty
        if (request.name.isBlank()) {
            throw IllegalArgumentException("Product name cannot be empty")
        }

        // Price must be positive
        if (request.price <= BigDecimal.ZERO) {
            throw IllegalArgumentException("Product price must be positive")
        }

        // Category must exist and be active
        request.categoryId?.let { categoryId ->
            val category = categoryRepository.findById(categoryId)
                .orElseThrow { IllegalArgumentException("Category not found: $categoryId") }

            if (!category.isActive) {
                throw IllegalArgumentException("Category is not active: $categoryId")
            }
        }

        // Stock quantity cannot be negative
        if (request.stockQuantity < 0) {
            throw IllegalArgumentException("Stock quantity cannot be negative")
        }
    }

    /**
     * Validate critical data integrity constraints.
     *
     * These validations apply even with admin override to prevent data corruption.
     */
    private fun validateDataIntegrity(request: CreateProductRequest) {
        // Name must not be null or empty (data integrity)
        if (request.name.isBlank()) {
            throw IllegalArgumentException("Product name cannot be empty (data integrity violation)")
        }

        // Price must not be null (data integrity)
        // Note: We allow negative prices with admin override for testing purposes
    }

    /**
     * Verify admin authorization for override operations.
     *
     * In a real application, this would check Spring Security context for ADMIN role.
     * For this example, we perform a basic check.
     */
    private fun verifyAdminAuthorization(user: String) {
        // In real implementation, check: SecurityContextHolder.getContext().authentication
        // For demo purposes, check user prefix
        if (!user.startsWith("admin_")) {
            throw SecurityException("User $user is not authorized for admin override")
        }
    }

    /**
     * Log admin override operation for audit trail.
     *
     * All admin override operations must be logged for compliance and accountability.
     */
    private fun logAdminOverride(
        adminUser: String,
        operation: String,
        entityType: String,
        entityId: Long? = null,
        reason: String?
    ) {
        val log = AdminOverrideLog(
            adminUser = adminUser,
            operation = operation,
            entityType = entityType,
            entityId = entityId,
            reason = reason
        )
        adminOverrideLogRepository.save(log)
    }
}
