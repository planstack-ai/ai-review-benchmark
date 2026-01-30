<?php

namespace App\Services;

use Carbon\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use App\Models\MonthlyReport;
use App\Models\Transaction;
use App\Exceptions\MonthEndProcessingException;

class MonthEndProcessingService
{
    public function __construct(
        private readonly MonthlyReport $monthlyReport,
        private readonly Transaction $transaction
    ) {}

    public function processMonthEnd(string $processingDate): array
    {
        $currentDate = Carbon::parse($processingDate);
        
        if (!$this->isValidProcessingDate($currentDate)) {
            throw new MonthEndProcessingException('Invalid processing date provided');
        }

        $results = [];
        
        DB::transaction(function () use ($currentDate, &$results) {
            $results['transactions_processed'] = $this->processTransactions($currentDate);
            $results['reports_generated'] = $this->generateMonthlyReports($currentDate);
            $results['next_processing_date'] = $this->calculateNextProcessingDate($currentDate);
        });

        Log::info('Month-end processing completed', $results);
        
        return $results;
    }

    private function isValidProcessingDate(Carbon $date): bool
    {
        return $date->isLastOfMonth() && $date->lessThanOrEqualTo(Carbon::now());
    }

    private function processTransactions(Carbon $processingDate): int
    {
        $startOfMonth = $processingDate->copy()->startOfMonth();
        $endOfMonth = $processingDate->copy()->endOfMonth();

        $transactions = $this->transaction
            ->whereBetween('created_at', [$startOfMonth, $endOfMonth])
            ->whereNull('processed_at')
            ->get();

        $processedCount = 0;

        foreach ($transactions as $transaction) {
            if ($this->validateTransaction($transaction)) {
                $transaction->update([
                    'processed_at' => $processingDate,
                    'status' => 'processed'
                ]);
                $processedCount++;
            }
        }

        return $processedCount;
    }

    private function validateTransaction($transaction): bool
    {
        return $transaction->amount > 0 && 
               !empty($transaction->reference_number) &&
               $transaction->status === 'pending';
    }

    private function generateMonthlyReports(Carbon $processingDate): int
    {
        $reportData = $this->aggregateMonthlyData($processingDate);
        
        $report = $this->monthlyReport->create([
            'period_start' => $processingDate->copy()->startOfMonth(),
            'period_end' => $processingDate->copy()->endOfMonth(),
            'total_transactions' => $reportData['transaction_count'],
            'total_amount' => $reportData['total_amount'],
            'average_amount' => $reportData['average_amount'],
            'generated_at' => $processingDate
        ]);

        return $report ? 1 : 0;
    }

    private function aggregateMonthlyData(Carbon $processingDate): array
    {
        $startOfMonth = $processingDate->copy()->startOfMonth();
        $endOfMonth = $processingDate->copy()->endOfMonth();

        $aggregates = $this->transaction
            ->whereBetween('created_at', [$startOfMonth, $endOfMonth])
            ->where('status', 'processed')
            ->selectRaw('COUNT(*) as transaction_count, SUM(amount) as total_amount, AVG(amount) as average_amount')
            ->first();

        return [
            'transaction_count' => $aggregates->transaction_count ?? 0,
            'total_amount' => $aggregates->total_amount ?? 0,
            'average_amount' => $aggregates->average_amount ?? 0
        ];
    }

    private function calculateNextProcessingDate(Carbon $currentDate): string
    {
        $nextMonth = $currentDate->addMonth();
        $nextProcessingDate = $nextMonth->endOfMonth();
        
        return $nextProcessingDate->format('Y-m-d');
    }

    public function getProcessingSchedule(int $monthsAhead = 12): array
    {
        $schedule = [];
        $currentDate = Carbon::now()->endOfMonth();

        for ($i = 0; $i < $monthsAhead; $i++) {
            $schedule[] = [
                'processing_date' => $currentDate->format('Y-m-d'),
                'month_name' => $currentDate->format('F Y'),
                'is_weekend' => $currentDate->isWeekend()
            ];
            
            $currentDate = $currentDate->addMonth()->endOfMonth();
        }

        return $schedule;
    }
}