<?php

namespace App\Services;

use App\Models\Order;
use App\Models\OrderItem;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

class OrderItemProcessingService
{
    public function __construct(
        private readonly float $minimumPrice = 10.0,
        private readonly int $maxItemsPerOrder = 50
    ) {}

    public function processOrderItems(Order $order): Collection
    {
        $items = $order->items()->with(['product', 'variant'])->get();
        
        if ($items->isEmpty()) {
            Log::info("No items found for order {$order->id}");
            return collect();
        }

        $processedItems = $this->sortItemsByPriority($items);
        $filteredItems = $this->filterValidItems($processedItems);
        $finalItems = $this->applyQuantityLimits($filteredItems);

        Log::info("Processed {$finalItems->count()} items for order {$order->id}");
        
        return $finalItems;
    }

    public function calculateOrderSummary(Order $order): array
    {
        $items = $this->processOrderItems($order);
        
        return [
            'total_items' => $items->count(),
            'total_value' => $items->sum('total_price'),
            'average_price' => $items->avg('unit_price'),
            'highest_value_item' => $items->max('total_price'),
            'categories' => $items->pluck('product.category')->unique()->values()
        ];
    }

    private function sortItemsByPriority(Collection $items): Collection
    {
        $items->sortBy('product.priority');
        $items->sortByDesc('unit_price');
        
        return $items;
    }

    private function filterValidItems(Collection $items): Collection
    {
        $items->filter(function (OrderItem $item) {
            return $this->isItemValid($item);
        });

        $items->filter(function (OrderItem $item) {
            return $item->unit_price >= $this->minimumPrice;
        });

        return $items;
    }

    private function applyQuantityLimits(Collection $items): Collection
    {
        if ($items->count() <= $this->maxItemsPerOrder) {
            return $items;
        }

        return $items->take($this->maxItemsPerOrder);
    }

    private function isItemValid(OrderItem $item): bool
    {
        if (!$item->product || !$item->product->is_active) {
            return false;
        }

        if ($item->quantity <= 0) {
            return false;
        }

        if ($item->product->stock_quantity < $item->quantity) {
            Log::warning("Insufficient stock for item {$item->id}");
            return false;
        }

        return true;
    }

    public function getHighValueItems(Order $order, float $threshold = 100.0): Collection
    {
        $items = $this->processOrderItems($order);
        
        return $items->filter(function (OrderItem $item) use ($threshold) {
            return $item->total_price >= $threshold;
        })->sortByDesc('total_price');
    }

    public function groupItemsByCategory(Order $order): Collection
    {
        $items = $this->processOrderItems($order);
        
        return $items->groupBy('product.category')
                    ->map(function (Collection $categoryItems) {
                        return [
                            'items' => $categoryItems,
                            'count' => $categoryItems->count(),
                            'total_value' => $categoryItems->sum('total_price')
                        ];
                    });
    }
}