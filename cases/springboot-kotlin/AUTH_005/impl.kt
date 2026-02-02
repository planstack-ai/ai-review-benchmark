package com.example.service

import org.springframework.stereotype.Service
import java.math.BigDecimal

@Service
class ProductPricingService(
    private val productRepository: ProductRepository,
    private val securityContext: SecurityContext
) {

    fun getProductPrice(productId: Long): PriceResponse {
        val product = productRepository.findById(productId)
            .orElseThrow { IllegalArgumentException("Product not found: $productId") }

        val currentUser = securityContext.getCurrentUser()

        val effectivePrice = determinePrice(product, currentUser)
        val savings = if (effectivePrice < product.regularPrice) {
            product.regularPrice.subtract(effectivePrice)
        } else {
            BigDecimal.ZERO
        }

        return PriceResponse(
            productId = productId,
            productName = product.name,
            regularPrice = product.regularPrice,
            effectivePrice = effectivePrice,
            savings = savings,
            isMemberPrice = effectivePrice == product.memberPrice
        )
    }

    private fun determinePrice(product: Product, currentUser: User?): BigDecimal {
        val memberPrice = product.memberPrice

        if (memberPrice != null) {
            return memberPrice
        }

        return product.regularPrice
    }

    fun getProductPrices(productIds: List<Long>): List<PriceResponse> {
        return productIds.map { getProductPrice(it) }
    }
}

data class PriceResponse(
    val productId: Long,
    val productName: String,
    val regularPrice: BigDecimal,
    val effectivePrice: BigDecimal,
    val savings: BigDecimal,
    val isMemberPrice: Boolean
)

data class User(
    val id: Long = 0,
    val email: String,
    val membershipType: MembershipType = MembershipType.GUEST,
    val isActive: Boolean = true
)

enum class MembershipType {
    GUEST, MEMBER, PREMIUM
}

data class Product(
    val id: Long = 0,
    val name: String,
    val regularPrice: BigDecimal,
    val memberPrice: BigDecimal?,
    val isMemberExclusive: Boolean = false
)

interface ProductRepository {
    fun findById(id: Long): java.util.Optional<Product>
}

interface SecurityContext {
    fun getCurrentUser(): User?
    fun isAuthenticated(): Boolean
}

fun MembershipType.isMember(): Boolean =
    this == MembershipType.MEMBER || this == MembershipType.PREMIUM
