package com.example.ecommerce.service

import com.example.ecommerce.client.WarehouseApiClient
import com.example.ecommerce.dto.WarehouseInventory
import com.example.ecommerce.entity.Inventory
import com.example.ecommerce.repository.InventoryRepository
import org.slf4j.LoggerFactory
import org.springframework.scheduling.annotation.Async
import org.springframework.scheduling.annotation.Scheduled
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
class InventorySyncService(
    private val warehouseApiClient: WarehouseApiClient,
    private val inventoryRepository: InventoryRepository
) {
    private val logger = LoggerFactory.getLogger(javaClass)

    @Scheduled(fixedRate = 60000)
    @Async
    fun syncInventoryFromWarehouse() {
        logger.info("Starting inventory sync from warehouse")

        try {
            val warehouseData = warehouseApiClient.getAllInventory()

            warehouseData.forEach { item ->
                updateLocalInventory(item)
            }

            logger.info("Inventory sync completed. Updated ${warehouseData.size} items")

        } catch (e: Exception) {
            logger.error("Inventory sync failed", e)
        }
    }

    @Transactional
    fun updateLocalInventory(warehouseItem: WarehouseInventory) {
        val localInventory = inventoryRepository.findByProductId(warehouseItem.productId)
            ?: Inventory(productId = warehouseItem.productId)

        localInventory.quantity = warehouseItem.quantity
        localInventory.lastSyncedAt = LocalDateTime.now()

        inventoryRepository.save(localInventory)
    }

    @Async
    @Transactional
    fun syncSingleProduct(productId: Long) {
        logger.info("Syncing inventory for product: $productId")

        val warehouseData = warehouseApiClient.getInventory(productId)

        val inventory = inventoryRepository.findByProductId(productId)
            ?: throw IllegalArgumentException("Product not found: $productId")

        inventory.quantity = warehouseData.quantity
        inventory.lastSyncedAt = LocalDateTime.now()

        inventoryRepository.save(inventory)

        logger.info("Product $productId inventory synced: ${warehouseData.quantity}")
    }

    @Scheduled(cron = "0 0 * * * *")
    @Async
    fun fullInventoryReconciliation() {
        logger.info("Starting full inventory reconciliation")

        val warehouseData = warehouseApiClient.getAllInventory()

        var updated = 0
        var created = 0

        warehouseData.forEach { item ->
            var local = inventoryRepository.findByProductId(item.productId)

            if (local == null) {
                local = Inventory(productId = item.productId)
                created++
            } else {
                updated++
            }

            local.quantity = item.quantity
            local.lastSyncedAt = LocalDateTime.now()
            inventoryRepository.save(local)
        }

        logger.info("Reconciliation completed. Created: $created, Updated: $updated")
    }

    fun checkAndReserveStock(productId: Long, quantity: Int): Boolean {
        val inventory = inventoryRepository.findByProductId(productId)
            ?: throw IllegalArgumentException("Product not found")

        return if (inventory.availableQuantity >= quantity) {
            inventory.reservedQuantity += quantity
            inventoryRepository.save(inventory)
            true
        } else {
            false
        }
    }
}
