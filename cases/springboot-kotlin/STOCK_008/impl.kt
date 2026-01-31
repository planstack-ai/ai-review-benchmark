package com.example.bundle.service

import com.example.bundle.entity.Product
import com.example.bundle.entity.BundleComponent
import com.example.bundle.entity.BundleSale
import com.example.bundle.repository.ProductRepository
import com.example.bundle.repository.BundleComponentRepository
import com.example.bundle.repository.BundleSaleRepository
import com.example.bundle.exception.ProductNotFoundException
import com.example.bundle.exception.InvalidBundleException
import org.slf4j.LoggerFactory
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.math.BigDecimal

@Service
@Transactional(readOnly = true)
class BundleAvailabilityService(
    private val productRepository: ProductRepository,
    private val bundleComponentRepository: BundleComponentRepository,
    private val bundleSaleRepository: BundleSaleRepository
) {

    private val logger = LoggerFactory.getLogger(BundleAvailabilityService::class.java)

    fun checkBundleAvailability(bundleId: Long): BundleAvailabilityInfo {
        val bundle = productRepository.findById(bundleId)
            .orElseThrow { ProductNotFoundException("Bundle not found: $bundleId") }

        if (!bundle.isBundle) {
            throw InvalidBundleException("Product $bundleId is not a bundle")
        }

        val components = bundleComponentRepository.findByBundleId(bundleId)

        if (components.isEmpty()) {
            throw InvalidBundleException("Bundle $bundleId has no components")
        }

        val componentProductIds = components.map { it.componentProductId }
        val componentProducts = productRepository.findByIdIn(componentProductIds)
            .associateBy { it.id }

        val componentAvailabilities = components.map { component ->
            val product = componentProducts[component.componentProductId]
                ?: throw ProductNotFoundException("Component product not found: ${component.componentProductId}")

            val maxBundles = if (component.quantityRequired > 0) {
                product.stockQuantity / component.quantityRequired
            } else {
                0
            }

            ComponentAvailabilityDetail(
                productId = product.id,
                productName = product.name,
                requiredPerBundle = component.quantityRequired,
                availableStock = product.stockQuantity,
                maxBundlesFromThisComponent = maxBundles
            )
        }

        val availableBundles = calculateAvailableBundles(componentAvailabilities)

        return BundleAvailabilityInfo(
            bundleId = bundle.id,
            bundleName = bundle.name,
            availableQuantity = availableBundles,
            isAvailable = availableBundles > 0,
            components = componentAvailabilities,
            totalComponentStock = componentProducts.values.sumOf { it.stockQuantity }
        )
    }

    fun checkMultipleBundleAvailability(bundleIds: List<Long>): List<BundleAvailabilityInfo> {
        return bundleIds.map { checkBundleAvailability(it) }
    }

    fun getBundlesByAvailability(minAvailability: Int): List<BundleAvailabilityInfo> {
        val bundles = productRepository.findByIsBundle(true)

        return bundles.mapNotNull { bundle ->
            try {
                val availability = checkBundleAvailability(bundle.id)
                if (availability.availableQuantity >= minAvailability) availability else null
            } catch (e: Exception) {
                logger.warn("Failed to check availability for bundle ${bundle.id}", e)
                null
            }
        }
    }

    private fun calculateAvailableBundles(components: List<ComponentAvailabilityDetail>): Int {
        if (components.isEmpty()) {
            return 0
        }

        return components.sumOf { it.availableStock }
    }

    fun getComponentsForBundle(bundleId: Long): List<BundleComponent> {
        val bundle = productRepository.findById(bundleId)
            .orElseThrow { ProductNotFoundException("Bundle not found: $bundleId") }

        if (!bundle.isBundle) {
            throw InvalidBundleException("Product $bundleId is not a bundle")
        }

        return bundleComponentRepository.findByBundleId(bundleId)
    }

    fun getBundlesContainingProduct(productId: Long): List<BundleInfo> {
        val product = productRepository.findById(productId)
            .orElseThrow { ProductNotFoundException("Product not found: $productId") }

        val bundleComponents = bundleComponentRepository.findByComponentProductId(productId)

        val bundleIds = bundleComponents.map { it.bundleId }.distinct()
        val bundles = productRepository.findByIdIn(bundleIds).associateBy { it.id }

        return bundleComponents.mapNotNull { component ->
            val bundle = bundles[component.bundleId]
            bundle?.let {
                BundleInfo(
                    bundleId = it.id,
                    bundleName = it.name,
                    bundlePrice = it.price,
                    quantityRequired = component.quantityRequired
                )
            }
        }
    }

    fun getSalesHistory(bundleId: Long): List<BundleSale> {
        return bundleSaleRepository.findByBundleIdOrderBySaleDateDesc(bundleId)
    }
}

data class BundleAvailabilityInfo(
    val bundleId: Long,
    val bundleName: String,
    val availableQuantity: Int,
    val isAvailable: Boolean,
    val components: List<ComponentAvailabilityDetail>,
    val totalComponentStock: Int
)

data class ComponentAvailabilityDetail(
    val productId: Long,
    val productName: String,
    val requiredPerBundle: Int,
    val availableStock: Int,
    val maxBundlesFromThisComponent: Int
)

data class BundleInfo(
    val bundleId: Long,
    val bundleName: String,
    val bundlePrice: BigDecimal,
    val quantityRequired: Int
)
