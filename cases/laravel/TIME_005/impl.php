<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\DailyReport;
use App\Models\Order;
use Illuminate\Support\Carbon;

class ReportService
{
    private const BUSINESS_TIMEZONE = 'America/New_York';

    public function generateDailyReport(string $date): array
    {
        // BUG: Uses the date directly without timezone conversion
        // If $date is "2024-01-15", this queries for UTC midnight to midnight
        // But we want business day: Jan 15 05:00 UTC to Jan 16 05:00 UTC (EST = UTC-5)
        $startOfDay = Carbon::parse($date)->startOfDay();
        $endOfDay = Carbon::parse($date)->endOfDay();

        $orders = Order::where('status', 'completed')
            ->whereBetween('created_at', [$startOfDay, $endOfDay])
            ->get();

        $orderCount = $orders->count();
        $totalRevenue = $orders->sum('total');
        $averageOrderValue = $orderCount > 0 ? $totalRevenue / $orderCount : 0;

        $report = DailyReport::updateOrCreate(
            ['report_date' => $date],
            [
                'order_count' => $orderCount,
                'total_revenue' => $totalRevenue,
                'average_order_value' => round($averageOrderValue, 2),
            ]
        );

        return [
            'success' => true,
            'report' => $report,
        ];
    }

    public function generateYesterdayReport(): array
    {
        // BUG: Uses server's "yesterday" (UTC) instead of business timezone yesterday
        $yesterday = now()->subDay()->toDateString();

        return $this->generateDailyReport($yesterday);
    }

    public function getReportForDateRange(string $startDate, string $endDate): array
    {
        $reports = DailyReport::whereBetween('report_date', [$startDate, $endDate])
            ->orderBy('report_date')
            ->get();

        return [
            'reports' => $reports,
            'total_orders' => $reports->sum('order_count'),
            'total_revenue' => $reports->sum('total_revenue'),
        ];
    }
}
