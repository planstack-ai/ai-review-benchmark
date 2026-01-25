<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use Illuminate\Support\Carbon;

class OrderReportService
{
    public function getOrderHistory(string $startDate, string $endDate, ?string $status = null): array
    {
        $query = Order::whereBetween('created_at', [$startDate, $endDate]);

        if ($status) {
            $query->where('status', $status);
        }

        // BUG: Fetches all orders into memory, then processes
        // For large date ranges, this can exhaust memory
        $orders = $query->get();

        $result = [];
        $totalRevenue = 0;

        foreach ($orders as $order) {
            // BUG: N+1 for order items
            $items = $order->items;
            $orderTotal = 0;

            $lineItems = [];
            foreach ($items as $item) {
                // BUG: N+1 for products
                $lineItems[] = [
                    'product_name' => $item->product->name,
                    'quantity' => $item->quantity,
                    'unit_price' => $item->unit_price,
                    'subtotal' => $item->quantity * $item->unit_price,
                ];
                $orderTotal += $item->quantity * $item->unit_price;
            }

            $result[] = [
                'order_id' => $order->id,
                'created_at' => $order->created_at,
                'status' => $order->status,
                'items' => $lineItems,
                'total' => $orderTotal,
            ];

            $totalRevenue += $orderTotal;
        }

        return [
            'orders' => $result,
            'summary' => [
                'order_count' => count($result),
                'total_revenue' => $totalRevenue,
            ],
        ];
    }

    public function getDailySummary(string $date): array
    {
        $start = Carbon::parse($date)->startOfDay();
        $end = Carbon::parse($date)->endOfDay();

        // BUG: Could use database aggregation instead of fetching all records
        $orders = Order::whereBetween('created_at', [$start, $end])->get();

        $statusCounts = [];
        foreach ($orders as $order) {
            $statusCounts[$order->status] = ($statusCounts[$order->status] ?? 0) + 1;
        }

        return [
            'date' => $date,
            'total_orders' => $orders->count(),
            'by_status' => $statusCounts,
        ];
    }
}
