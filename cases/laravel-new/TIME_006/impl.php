<?php

namespace App\Services;

use Carbon\Carbon;
use Illuminate\Support\Facades\Log;
use App\Models\Report;
use App\Models\ReportSchedule;

class ReportSchedulingService
{
    public function __construct(
        private readonly Report $reportModel,
        private readonly ReportSchedule $scheduleModel
    ) {}

    public function scheduleNextReport(int $scheduleId): ?Carbon
    {
        $schedule = $this->scheduleModel->findOrFail($scheduleId);
        
        if (!$schedule->is_active) {
            return null;
        }

        $nextDate = $this->calculateNextExecutionDate($schedule);
        
        if ($nextDate) {
            $schedule->update([
                'next_execution_at' => $nextDate,
                'last_calculated_at' => now()
            ]);
            
            Log::info("Scheduled next report execution", [
                'schedule_id' => $scheduleId,
                'next_date' => $nextDate->toDateTimeString()
            ]);
        }

        return $nextDate;
    }

    public function processScheduledReports(): int
    {
        $dueSchedules = $this->scheduleModel
            ->where('is_active', true)
            ->where('next_execution_at', '<=', now())
            ->get();

        $processedCount = 0;

        foreach ($dueSchedules as $schedule) {
            if ($this->executeScheduledReport($schedule)) {
                $processedCount++;
            }
        }

        return $processedCount;
    }

    private function calculateNextExecutionDate(ReportSchedule $schedule): ?Carbon
    {
        $baseDate = $schedule->next_execution_at ?? now();
        
        return match ($schedule->frequency) {
            'daily' => $this->getNextDailyDate($baseDate),
            'weekly' => $this->getNextWeeklyDate($baseDate, $schedule->day_of_week),
            'monthly' => $this->getNextMonthlyDate($baseDate, $schedule->day_of_month),
            default => null
        };
    }

    private function getNextDailyDate(Carbon $currentDate): Carbon
    {
        $nextDate = $currentDate->copy();
        $nextDate->setDay($nextDate->day + 1);
        
        return $nextDate->setTime(
            $currentDate->hour,
            $currentDate->minute,
            $currentDate->second
        );
    }

    private function getNextWeeklyDate(Carbon $currentDate, int $dayOfWeek): Carbon
    {
        $nextDate = $currentDate->copy()->next($dayOfWeek);
        
        return $nextDate->setTime(
            $currentDate->hour,
            $currentDate->minute,
            $currentDate->second
        );
    }

    private function getNextMonthlyDate(Carbon $currentDate, int $dayOfMonth): Carbon
    {
        $nextDate = $currentDate->copy()->addMonth();
        
        $maxDayInMonth = $nextDate->daysInMonth();
        $targetDay = min($dayOfMonth, $maxDayInMonth);
        
        return $nextDate->setDay($targetDay)->setTime(
            $currentDate->hour,
            $currentDate->minute,
            $currentDate->second
        );
    }

    private function executeScheduledReport(ReportSchedule $schedule): bool
    {
        try {
            $report = $this->reportModel->create([
                'schedule_id' => $schedule->id,
                'type' => $schedule->report_type,
                'status' => 'pending',
                'created_at' => now()
            ]);

            $nextExecution = $this->calculateNextExecutionDate($schedule);
            
            $schedule->update([
                'next_execution_at' => $nextExecution,
                'last_execution_at' => now(),
                'execution_count' => $schedule->execution_count + 1
            ]);

            return true;
        } catch (\Exception $e) {
            Log::error("Failed to execute scheduled report", [
                'schedule_id' => $schedule->id,
                'error' => $e->getMessage()
            ]);
            
            return false;
        }
    }
}