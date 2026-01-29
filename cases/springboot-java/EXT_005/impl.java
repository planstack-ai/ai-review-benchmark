package com.example.ecommerce.service;

import com.example.ecommerce.client.WarehouseApiClient;
import com.example.ecommerce.dto.WarehouseInventory;
import com.example.ecommerce.entity.Inventory;
import com.example.ecommerce.repository.InventoryRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Async;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class InventorySyncService {

    private static final Logger logger = LoggerFactory.getLogger(InventorySyncService.class);

    @Autowired
    private WarehouseApiClient warehouseApiClient;

    @Autowired
    private InventoryRepository inventoryRepository;

    @Scheduled(fixedRate = 60000)
    @Async
    public void syncInventoryFromWarehouse() {
        logger.info("Starting inventory sync from warehouse");

        try {
            List<WarehouseInventory> warehouseData = warehouseApiClient.getAllInventory();

            for (WarehouseInventory item : warehouseData) {
                updateLocalInventory(item);
            }

            logger.info("Inventory sync completed. Updated {} items", warehouseData.size());

        } catch (Exception e) {
            logger.error("Inventory sync failed", e);
        }
    }

    @Transactional
    public void updateLocalInventory(WarehouseInventory warehouseItem) {
        Inventory localInventory = inventoryRepository.findByProductId(warehouseItem.getProductId())
                .orElse(null);

        if (localInventory == null) {
            localInventory = new Inventory();
            localInventory.setProductId(warehouseItem.getProductId());
        }

        localInventory.setQuantity(warehouseItem.getQuantity());
        localInventory.setLastSyncedAt(LocalDateTime.now());

        inventoryRepository.save(localInventory);
    }

    @Async
    @Transactional
    public void syncSingleProduct(Long productId) {
        logger.info("Syncing inventory for product: {}", productId);

        WarehouseInventory warehouseData = warehouseApiClient.getInventory(productId);

        Inventory inventory = inventoryRepository.findByProductId(productId)
                .orElseThrow(() -> new IllegalArgumentException("Product not found: " + productId));

        inventory.setQuantity(warehouseData.getQuantity());
        inventory.setLastSyncedAt(LocalDateTime.now());

        inventoryRepository.save(inventory);

        logger.info("Product {} inventory synced: {}", productId, warehouseData.getQuantity());
    }

    @Scheduled(cron = "0 0 * * * *")
    @Async
    public void fullInventoryReconciliation() {
        logger.info("Starting full inventory reconciliation");

        List<WarehouseInventory> warehouseData = warehouseApiClient.getAllInventory();

        int updated = 0;
        int created = 0;

        for (WarehouseInventory item : warehouseData) {
            Inventory local = inventoryRepository.findByProductId(item.getProductId()).orElse(null);

            if (local == null) {
                local = new Inventory();
                local.setProductId(item.getProductId());
                created++;
            } else {
                updated++;
            }

            local.setQuantity(item.getQuantity());
            local.setLastSyncedAt(LocalDateTime.now());
            inventoryRepository.save(local);
        }

        logger.info("Reconciliation completed. Created: {}, Updated: {}", created, updated);
    }

    public boolean checkAndReserveStock(Long productId, int quantity) {
        Inventory inventory = inventoryRepository.findByProductId(productId)
                .orElseThrow(() -> new IllegalArgumentException("Product not found"));

        if (inventory.getAvailableQuantity() >= quantity) {
            inventory.setReservedQuantity(inventory.getReservedQuantity() + quantity);
            inventoryRepository.save(inventory);
            return true;
        }

        return false;
    }
}
