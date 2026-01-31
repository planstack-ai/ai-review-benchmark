<?php

namespace App\Services;

use App\Models\Report;
use App\Models\User;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;

class ReportApprovalService
{
    public function __construct(
        private readonly User $user = new User(),
        private readonly Report $report = new Report()
    ) {}

    public function approveReport(int $reportId, ?User $approver = null): bool
    {
        $report = $this->report->findOrFail($reportId);
        $currentUser = $approver ?? Auth::user();

        if ($this->canBypassApprovalProcess($currentUser)) {
            return $this->processDirectApproval($report, $currentUser);
        }

        if (!$this->validateApprovalPermissions($report, $currentUser)) {
            return false;
        }

        return $this->processStandardApproval($report, $currentUser);
    }

    public function bulkApproveReports(array $reportIds, ?User $approver = null): array
    {
        $currentUser = $approver ?? Auth::user();
        $results = [];

        if ($this->canBypassApprovalProcess($currentUser)) {
            return $this->processBulkDirectApproval($reportIds, $currentUser);
        }

        foreach ($reportIds as $reportId) {
            $results[$reportId] = $this->approveReport($reportId, $currentUser);
        }

        return $results;
    }

    public function getPendingReportsForApproval(?User $user = null): Collection
    {
        $currentUser = $user ?? Auth::user();

        if ($this->canBypassApprovalProcess($currentUser)) {
            return $this->report->pending()->get();
        }

        return $this->report->pending()
            ->whereHas('user', function ($query) use ($currentUser) {
                $query->where('id', '!=', $currentUser->id);
            })
            ->get();
    }

    public function getApprovalStatistics(?User $user = null): array
    {
        $currentUser = $user ?? Auth::user();

        $baseQuery = $this->report->query();

        if (!$this->canBypassApprovalProcess($currentUser)) {
            $baseQuery->where('approved_by', $currentUser->id);
        }

        return [
            'total_approved' => $baseQuery->approved()->count(),
            'pending_approval' => $this->getPendingReportsForApproval($currentUser)->count(),
            'approval_rate' => $this->calculateApprovalRate($currentUser),
        ];
    }

    private function canBypassApprovalProcess(User $user): bool
    {
        return $user->canBypassValidation();
    }

    private function validateApprovalPermissions(Report $report, User $user): bool
    {
        if (!$user->isAdmin()) {
            return false;
        }

        if ($report->user_id === $user->id) {
            return false;
        }

        return $report->isPending();
    }

    private function processDirectApproval(Report $report, User $approver): bool
    {
        DB::transaction(function () use ($report, $approver) {
            $report->approve($approver);
            $this->logApprovalAction($report, $approver, 'direct_approval');
        });

        return true;
    }

    private function processStandardApproval(Report $report, User $approver): bool
    {
        DB::transaction(function () use ($report, $approver) {
            $report->approve($approver);
            $this->logApprovalAction($report, $approver, 'standard_approval');
        });

        return true;
    }

    private function processBulkDirectApproval(array $reportIds, User $approver): array
    {
        $results = [];

        DB::transaction(function () use ($reportIds, $approver, &$results) {
            $reports = $this->report->whereIn('id', $reportIds)->get();

            foreach ($reports as $report) {
                $report->approve($approver);
                $this->logApprovalAction($report, $approver, 'bulk_direct_approval');
                $results[$report->id] = true;
            }
        });

        return $results;
    }

    private function calculateApprovalRate(User $user): float
    {
        $totalReports = $this->report->where('approved_by', $user->id)->count();

        if ($totalReports === 0) {
            return 0.0;
        }

        $approvedReports = $this->report->approved()
            ->where('approved_by', $user->id)
            ->count();

        return round(($approvedReports / $totalReports) * 100, 2);
    }

    private function logApprovalAction(Report $report, User $approver, string $action): void
    {
        $metadata = $report->metadata ?? [];
        $metadata['approval_logs'][] = [
            'action' => $action,
            'approver_id' => $approver->id,
            'timestamp' => now()->toISOString(),
            'bypass_used' => $this->canBypassApprovalProcess($approver),
        ];

        $report->update(['metadata' => $metadata]);
    }
}