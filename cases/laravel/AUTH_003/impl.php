<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use Illuminate\Support\Collection;

class OrderReportService
{
    private ?array $dateRange;
    private ?string $statusFilter;
    private ?Collection $filteredOrders = null;

    public function __construct(?array $dateRange = null, ?string $statusFilter = null)
    {
        $this->dateRange = $dateRange;
        $this->statusFilter = $statusFilter;
    }

    public function generateReport(): array
    {
        return [
            'total_orders' => $this->getFilteredOrders()->count(),
            'total_revenue' => $this->calculateTotalRevenue(),
            'orders_by_status' => $this->groupOrdersByStatus(),
            'top_customers' => $this->findTopCustomers(),
            'average_order_value' => $this->calculateAverageOrderValue(),
        ];
    }

    public function exportOrdersCsv(): string
    {
        $csv = implode(',', $this->csvHeaders()) . "\n";

        foreach ($this->getFilteredOrders()->with(['user', 'orderItems'])->cursor() as $order) {
            $csv .= implode(',', $this->formatOrderRow($order)) . "\n";
        }

        return $csv;
    }

    public function recentOrdersSummary(int $limit = 50): array
    {
        $recentOrders = $this->getFilteredOrders()
            ->orderBy('created_at', 'desc')
            ->limit($limit)
            ->get();

        return [
            'orders' => $recentOrders->map(fn($order) => $this->formatOrderSummary($order)),
            'summary_stats' => $this->calculateSummaryStats($recentOrders),
        ];
    }

    private function getFilteredOrders()
    {
        if ($this->filteredOrders === null) {
            $query = $this->orders();

            if ($this->dateRange) {
                $query->whereBetween('created_at', $this->dateRange);
            }

            if ($this->statusFilter) {
                $query->where('status', $this->statusFilter);
            }

            $this->filteredOrders = $query;
        }

        return $this->filteredOrders;
    }

    private function orders()
    {
        return Order::with(['user', 'orderItems']);
    }

    private function calculateTotalRevenue(): float
    {
        return $this->getFilteredOrders()->sum('total_amount');
    }

    private function groupOrdersByStatus(): array
    {
        return $this->getFilteredOrders()
            ->toBase()
            ->groupBy('status')
            ->map->count()
            ->toArray();
    }

    private function findTopCustomers(): Collection
    {
        return $this->getFilteredOrders()
            ->join('users', 'orders.user_id', '=', 'users.id')
            ->selectRaw('users.id, users.email, COUNT(*) as order_count, SUM(orders.total_amount) as total_spent')
            ->groupBy('users.id', 'users.email')
            ->orderByDesc('total_spent')
            ->limit(10)
            ->get();
    }

    private function calculateAverageOrderValue(): float
    {
        $totalRevenue = $this->calculateTotalRevenue();
        $orderCount = $this->getFilteredOrders()->count();

        if ($orderCount === 0) {
            return 0.0;
        }

        return round($totalRevenue / $orderCount, 2);
    }

    private function csvHeaders(): array
    {
        return ['Order ID', 'Customer Email', 'Status', 'Total Amount', 'Created At'];
    }

    private function formatOrderRow(Order $order): array
    {
        return [
            $order->id,
            $order->user?->email ?? 'N/A',
            $order->status,
            $order->total_amount,
            $order->created_at->format('Y-m-d H:i:s'),
        ];
    }

    private function formatOrderSummary(Order $order): array
    {
        return [
            'id' => $order->id,
            'customer_email' => $order->user?->email,
            'status' => $order->status,
            'total_amount' => $order->total_amount,
            'created_at' => $order->created_at,
        ];
    }

    private function calculateSummaryStats(Collection $orders): array
    {
        return [
            'total_count' => $orders->count(),
            'total_value' => $orders->sum('total_amount'),
            'status_breakdown' => $orders->groupBy('status')->map->count(),
        ];
    }
}
