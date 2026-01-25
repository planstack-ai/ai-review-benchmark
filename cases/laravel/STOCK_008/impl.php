<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Product;
use App\Models\PurchaseOrder;
use App\Models\Supplier;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

class ReorderService
{
    public function checkAndReorder(): array
    {
        $productsToReorder = $this->getProductsBelowReorderPoint();

        $ordersCreated = [];
        $skipped = [];

        foreach ($productsToReorder as $product) {
            $result = $this->createReorderIfNeeded($product);

            if ($result['created']) {
                $ordersCreated[] = $result['order'];
            } else {
                $skipped[] = [
                    'product_id' => $product->id,
                    'reason' => $result['reason'],
                ];
            }
        }

        return [
            'orders_created' => count($ordersCreated),
            'skipped' => count($skipped),
            'details' => [
                'orders' => $ordersCreated,
                'skipped' => $skipped,
            ],
        ];
    }

    private function getProductsBelowReorderPoint(): Collection
    {
        // BUG: Uses stock_quantity instead of availableStock (stock_quantity - reserved_quantity)
        // Reserved stock should not count toward available inventory
        return Product::whereRaw('stock_quantity <= reorder_point')->get();
    }

    private function createReorderIfNeeded(Product $product): array
    {
        // Check for existing pending PO
        $existingPO = PurchaseOrder::where('product_id', $product->id)
            ->whereIn('status', ['pending', 'confirmed', 'shipped'])
            ->first();

        if ($existingPO) {
            return [
                'created' => false,
                'reason' => 'Existing PO pending',
            ];
        }

        $reorderQuantity = $this->calculateReorderQuantity($product);

        if ($reorderQuantity <= 0) {
            return [
                'created' => false,
                'reason' => 'Calculated quantity is zero or negative',
            ];
        }

        $supplier = $this->findSupplier($product);

        if (!$supplier) {
            Log::warning("No supplier found for product {$product->id}");
            return [
                'created' => false,
                'reason' => 'No supplier available',
            ];
        }

        $order = PurchaseOrder::create([
            'product_id' => $product->id,
            'supplier_id' => $supplier->id,
            'quantity' => $reorderQuantity,
            'status' => 'pending',
            'expected_date' => now()->addDays($product->lead_time_days),
        ]);

        Log::info("Created PO {$order->id} for product {$product->id}, qty: {$reorderQuantity}");

        return [
            'created' => true,
            'order' => $order,
        ];
    }

    private function calculateReorderQuantity(Product $product): int
    {
        // Formula: (daily_demand * lead_time) + safety_stock - current_stock
        $targetStock = ($product->daily_demand * $product->lead_time_days) + $product->safety_stock;

        // BUG: Uses stock_quantity instead of availableStock()
        $currentStock = $product->stock_quantity;

        return max(0, (int) ceil($targetStock - $currentStock));
    }

    private function findSupplier(Product $product): ?Supplier
    {
        if ($product->primarySupplier && $product->primarySupplier->active) {
            return $product->primarySupplier;
        }

        return Supplier::where('active', true)->first();
    }
}
