<?php

namespace App\Services;

use App\Models\Product;
use App\Models\InventorySync;
use App\Models\Order;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;
use Carbon\Carbon;

class InventoryAvailabilityService
{
    public function __construct(
        private readonly WarehouseApiService $warehouseApi,
        private readonly int $syncDelayMinutes = 15
    ) {}

    public function checkProductAvailability(int $productId, int $requestedQuantity): bool
    {
        $product = Product::findOrFail($productId);
        
        if (!$product->track_inventory) {
            return true;
        }

        $availableStock = $this->calculateAvailableStock($product);
        
        return $availableStock >= $requestedQuantity;
    }

    public function getAvailableQuantity(int $productId): int
    {
        $product = Product::findOrFail($productId);
        
        if (!$product->track_inventory) {
            return PHP_INT_MAX;
        }

        return max(0, $this->calculateAvailableStock($product));
    }

    public function reserveStock(int $productId, int $quantity): bool
    {
        $product = Product::findOrFail($productId);
        
        if (!$this->checkProductAvailability($productId, $quantity)) {
            return false;
        }

        $product->decrement('local_stock', $quantity);
        
        $this->logStockReservation($productId, $quantity);
        
        return true;
    }

    private function calculateAvailableStock(Product $product): int
    {
        $localStock = $product->local_stock;
        $reservedStock = $this->getReservedStock($product->id);
        
        $available = $localStock - $reservedStock;
        
        return max(0, $available);
    }

    private function getReservedStock(int $productId): int
    {
        return Cache::remember(
            "reserved_stock_{$productId}",
            300,
            fn() => Order::where('product_id', $productId)
                ->where('status', 'pending')
                ->sum('quantity')
        );
    }

    private function getPendingSyncQuantity(int $productId): int
    {
        $cutoffTime = Carbon::now()->subMinutes($this->syncDelayMinutes);
        
        return InventorySync::where('product_id', $productId)
            ->where('status', 'pending')
            ->where('created_at', '>=', $cutoffTime)
            ->sum('quantity_change');
    }

    private function shouldTriggerWarehouseSync(Product $product): bool
    {
        $lastSync = $product->last_warehouse_sync_at;
        
        if (!$lastSync) {
            return true;
        }

        return $lastSync->diffInMinutes(Carbon::now()) >= $this->syncDelayMinutes;
    }

    private function logStockReservation(int $productId, int $quantity): void
    {
        Log::info('Stock reserved', [
            'product_id' => $productId,
            'quantity' => $quantity,
            'timestamp' => Carbon::now()->toISOString()
        ]);
    }

    public function syncWithWarehouse(int $productId): void
    {
        $product = Product::findOrFail($productId);
        
        try {
            $warehouseStock = $this->warehouseApi->getStockLevel($product->sku);
            
            InventorySync::create([
                'product_id' => $productId,
                'quantity_change' => $warehouseStock - $product->local_stock,
                'status' => 'pending',
                'source' => 'warehouse_api'
            ]);
            
            $product->update(['last_warehouse_sync_at' => Carbon::now()]);
            
        } catch (\Exception $e) {
            Log::error('Warehouse sync failed', [
                'product_id' => $productId,
                'error' => $e->getMessage()
            ]);
        }
    }
}