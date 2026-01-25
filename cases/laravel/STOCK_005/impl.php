<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\BundleComponent;
use App\Models\Product;
use Illuminate\Support\Facades\DB;

class BundleStockService
{
    public function checkBundleAvailability(int $bundleId, int $requestedQuantity): array
    {
        $bundle = Product::with('bundleComponents.component')->findOrFail($bundleId);

        if (!$bundle->isBundle()) {
            return [
                'available' => false,
                'message' => 'Product is not a bundle',
            ];
        }

        $maxAvailable = PHP_INT_MAX;

        foreach ($bundle->bundleComponents as $bundleComponent) {
            $component = $bundleComponent->component;
            $availablePerComponent = floor($component->availableStock() / $bundleComponent->quantity);
            $maxAvailable = min($maxAvailable, $availablePerComponent);
        }

        return [
            'available' => $maxAvailable >= $requestedQuantity,
            'max_available' => (int) $maxAvailable,
            'requested' => $requestedQuantity,
        ];
    }

    public function reserveBundleStock(int $bundleId, int $quantity): array
    {
        $bundle = Product::with('bundleComponents')->findOrFail($bundleId);

        if (!$bundle->isBundle()) {
            return [
                'success' => false,
                'message' => 'Product is not a bundle',
            ];
        }

        // BUG: Checks availability first, then reserves without transaction
        // Another request could consume stock between check and reserve
        $availability = $this->checkBundleAvailability($bundleId, $quantity);

        if (!$availability['available']) {
            return [
                'success' => false,
                'message' => 'Insufficient stock for bundle',
            ];
        }

        // BUG: Each component reserved separately without atomic transaction
        // If one fails, previous reservations are not rolled back
        foreach ($bundle->bundleComponents as $bundleComponent) {
            $componentQuantity = $bundleComponent->quantity * $quantity;

            $component = Product::find($bundleComponent->component_id);
            $component->reserved_quantity += $componentQuantity;
            $component->save();
        }

        return [
            'success' => true,
            'reserved_quantity' => $quantity,
        ];
    }

    public function releaseBundleStock(int $bundleId, int $quantity): array
    {
        $bundle = Product::with('bundleComponents')->findOrFail($bundleId);

        if (!$bundle->isBundle()) {
            return [
                'success' => false,
                'message' => 'Product is not a bundle',
            ];
        }

        DB::transaction(function () use ($bundle, $quantity) {
            foreach ($bundle->bundleComponents as $bundleComponent) {
                $componentQuantity = $bundleComponent->quantity * $quantity;

                Product::where('id', $bundleComponent->component_id)
                    ->decrement('reserved_quantity', $componentQuantity);
            }
        });

        return [
            'success' => true,
            'released_quantity' => $quantity,
        ];
    }
}
