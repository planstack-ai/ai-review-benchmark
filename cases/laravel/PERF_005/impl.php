<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Order;
use Illuminate\Support\Facades\Storage;

class DataExportService
{
    public function exportOrders(string $startDate, string $endDate): string
    {
        // BUG: Loads ALL matching orders into memory at once
        // For large date ranges, this exhausts memory
        $orders = Order::with('user')
            ->whereBetween('created_at', [$startDate, $endDate])
            ->get();

        $csv = "ID,Customer Name,Customer Email,Total,Status,Created At\n";

        foreach ($orders as $order) {
            // BUG: String concatenation for large data is inefficient
            // Creates many intermediate strings, causes memory fragmentation
            $csv .= implode(',', [
                $order->id,
                '"' . str_replace('"', '""', $order->user->name) . '"',
                $order->user->email,
                $order->total,
                $order->status,
                $order->created_at->toISOString(),
            ]) . "\n";
        }

        $filename = "orders_export_" . now()->format('Y-m-d_H-i-s') . ".csv";
        Storage::put("exports/{$filename}", $csv);

        return $filename;
    }

    public function exportAllUsers(): string
    {
        // BUG: No chunking or streaming for potentially huge dataset
        $users = \App\Models\User::all();

        $data = [];
        foreach ($users as $user) {
            $data[] = [
                $user->id,
                $user->name,
                $user->email,
                $user->created_at,
            ];
        }

        // BUG: Building entire CSV in memory
        $csv = "ID,Name,Email,Created At\n";
        foreach ($data as $row) {
            $csv .= implode(',', $row) . "\n";
        }

        $filename = "users_export_" . now()->format('Y-m-d_H-i-s') . ".csv";
        Storage::put("exports/{$filename}", $csv);

        return $filename;
    }
}
