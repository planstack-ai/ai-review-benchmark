<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use App\Models\Product;
use Illuminate\Support\Carbon;

class DashboardService
{
    public function getStatistics(): array
    {
        // BUG: Makes multiple separate queries when could be combined
        // Each count() is a separate database round-trip
        $pendingOrders = Order::where('status', 'pending')->count();
        $processingOrders = Order::where('status', 'processing')->count();
        $shippedOrders = Order::where('status', 'shipped')->count();
        $completedOrders = Order::where('status', 'completed')->count();

        // BUG: Fetches all orders just to sum totals
        // Should use database aggregation
        $allOrders = Order::all();
        $totalRevenue = $allOrders->sum('total');
        $averageOrderValue = $allOrders->avg('total');

        // BUG: Another query that could be combined
        $todayOrders = Order::whereDate('created_at', today())->count();

        return [
            'orders' => [
                'pending' => $pendingOrders,
                'processing' => $processingOrders,
                'shipped' => $shippedOrders,
                'completed' => $completedOrders,
                'today' => $todayOrders,
            ],
            'revenue' => [
                'total' => $totalRevenue,
                'average' => $averageOrderValue,
            ],
        ];
    }

    public function getInventoryStats(): array
    {
        // BUG: Loads all products into memory to count/sum
        $products = Product::all();

        return [
            'total_products' => $products->count(),
            'total_stock_value' => $products->sum(function ($p) {
                return $p->price * $p->stock;
            }),
            'low_stock_count' => $products->where('stock', '<', 10)->count(),
            'out_of_stock' => $products->where('stock', 0)->count(),
        ];
    }

    public function getRecentOrders(int $limit = 10): array
    {
        // BUG: N+1 for user relationship
        $orders = Order::orderBy('created_at', 'desc')
            ->limit($limit)
            ->get();

        return $orders->map(function ($order) {
            return [
                'id' => $order->id,
                'customer' => $order->user->name, // N+1 here
                'total' => $order->total,
                'status' => $order->status,
                'created_at' => $order->created_at,
            ];
        })->toArray();
    }
}
