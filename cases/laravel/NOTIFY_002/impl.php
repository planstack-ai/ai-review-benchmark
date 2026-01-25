<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Product;
use App\Models\User;
use App\Notifications\LowStockAlertNotification;
use Illuminate\Support\Facades\Notification;

class StockAlertService
{
    private const ALERT_COOLDOWN_HOURS = 24;

    public function checkAndAlert(): array
    {
        $lowStockProducts = Product::whereRaw('stock_quantity < reorder_point')->get();

        $alertsSent = 0;

        foreach ($lowStockProducts as $product) {
            if ($this->shouldSendAlert($product)) {
                $this->sendLowStockAlert($product);
                $alertsSent++;
            }
        }

        return [
            'low_stock_count' => $lowStockProducts->count(),
            'alerts_sent' => $alertsSent,
        ];
    }

    private function shouldSendAlert(Product $product): bool
    {
        if (!$product->last_low_stock_alert_at) {
            return true;
        }

        // BUG: Uses gte (greater than or equal) instead of gt (greater than)
        // This means alert is sent again immediately after exactly 24 hours
        // Combined with the update below, can cause double alerts
        $hoursSinceLastAlert = $product->last_low_stock_alert_at->diffInHours(now());

        return $hoursSinceLastAlert >= self::ALERT_COOLDOWN_HOURS;
    }

    private function sendLowStockAlert(Product $product): void
    {
        $managers = User::where('role', 'inventory_manager')->get();

        // BUG: Updates timestamp before sending notification
        // If notification fails, timestamp is already updated
        // Next check will skip this product even though alert wasn't sent
        $product->update(['last_low_stock_alert_at' => now()]);

        Notification::send($managers, new LowStockAlertNotification($product));
    }

    public function checkSingleProduct(int $productId): array
    {
        $product = Product::findOrFail($productId);

        if ($product->stock_quantity >= $product->reorder_point) {
            return [
                'low_stock' => false,
                'message' => 'Stock level is adequate',
            ];
        }

        if (!$this->shouldSendAlert($product)) {
            return [
                'low_stock' => true,
                'alert_sent' => false,
                'message' => 'Alert already sent recently',
            ];
        }

        $this->sendLowStockAlert($product);

        return [
            'low_stock' => true,
            'alert_sent' => true,
        ];
    }

    public function clearAlertStatus(int $productId): void
    {
        Product::where('id', $productId)
            ->where('stock_quantity', '>=', \DB::raw('reorder_point'))
            ->update(['last_low_stock_alert_at' => null]);
    }
}
