<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\FlashSale;
use App\Models\FlashSaleItem;
use App\Models\Product;
use Illuminate\Support\Carbon;

class FlashSaleService
{
    public function createSale(string $name, string $startsAt, string $endsAt, string $timezone): array
    {
        // BUG: Parses time in given timezone but doesn't convert to UTC before storing
        // Laravel will store it as-is, treating it as UTC
        $start = Carbon::parse($startsAt, $timezone);
        $end = Carbon::parse($endsAt, $timezone);

        if ($start->gte($end)) {
            return [
                'success' => false,
                'message' => 'End time must be after start time',
            ];
        }

        $sale = FlashSale::create([
            'name' => $name,
            'starts_at' => $start,
            'ends_at' => $end,
        ]);

        return ['success' => true, 'sale' => $sale];
    }

    public function isSaleActive(int $saleId): bool
    {
        $sale = FlashSale::find($saleId);

        if (!$sale || !$sale->active) {
            return false;
        }

        $now = now(); // Returns UTC time

        // Comparison will be wrong if starts_at/ends_at were stored with wrong timezone
        return $now->gte($sale->starts_at) && $now->lt($sale->ends_at);
    }

    public function getActiveFlashPrice(int $productId): ?float
    {
        $now = now();

        $saleItem = FlashSaleItem::whereHas('flashSale', function ($query) use ($now) {
            $query->where('active', true)
                ->where('starts_at', '<=', $now)
                ->where('ends_at', '>', $now);
        })
            ->where('product_id', $productId)
            ->first();

        if (!$saleItem) {
            return null;
        }

        if ($saleItem->quantity_limit && $saleItem->sold_count >= $saleItem->quantity_limit) {
            return null;
        }

        return (float) $saleItem->sale_price;
    }

    public function purchaseFlashItem(int $saleItemId, int $quantity): array
    {
        $item = FlashSaleItem::with('flashSale')->findOrFail($saleItemId);

        if (!$this->isSaleActive($item->flash_sale_id)) {
            return [
                'success' => false,
                'message' => 'Sale is not currently active',
            ];
        }

        if ($item->quantity_limit) {
            $remaining = $item->quantity_limit - $item->sold_count;
            if ($quantity > $remaining) {
                return [
                    'success' => false,
                    'message' => 'Not enough sale items remaining',
                ];
            }
        }

        $item->increment('sold_count', $quantity);

        return [
            'success' => true,
            'price' => $item->sale_price,
            'quantity' => $quantity,
        ];
    }
}
