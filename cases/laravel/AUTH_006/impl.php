<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use Illuminate\Support\Collection;

class PointsAccessService
{
    private ?User $currentUser;
    private array $params;
    private array $errors = [];

    public function __construct(?User $currentUser, array $params = [])
    {
        $this->currentUser = $currentUser;
        $this->params = $params;
    }

    public function execute(): array
    {
        if (!$this->currentUser) {
            return $this->failureResult('User not authenticated');
        }

        return match ($this->params['action'] ?? null) {
            'show' => $this->showPoints(),
            'list' => $this->listUserPoints(),
            'summary' => $this->pointsSummary(),
            default => $this->failureResult('Invalid action specified'),
        };
    }

    private function showPoints(): array
    {
        $targetUser = $this->findTargetUser();

        if (!$targetUser) {
            return $this->failureResult('User not found');
        }

        $points = $this->fetchUserPoints($targetUser);

        return $this->successResult($this->formatPointsData($points));
    }

    private function listUserPoints(): array
    {
        $targetUser = $this->findTargetUser();

        if (!$targetUser) {
            return $this->failureResult('User not found');
        }

        $points = $this->fetchUserPoints($targetUser);
        $paginatedPoints = $this->paginatePoints($points);

        return $this->successResult([
            'points' => $this->formatPointsCollection($paginatedPoints),
            'total_count' => $points->count(),
            'page' => $this->currentPage(),
        ]);
    }

    private function pointsSummary(): array
    {
        $targetUser = $this->findTargetUser();

        if (!$targetUser) {
            return $this->failureResult('User not found');
        }

        $points = $this->fetchUserPoints($targetUser);

        return $this->successResult([
            'total_points' => $this->calculateTotalPoints($points),
            'categories' => $this->groupPointsByCategory($points),
            'recent_activity' => $this->recentPointsActivity($points),
        ]);
    }

    private function findTargetUser(): ?User
    {
        $userId = $this->params['user_id'] ?? $this->currentUser->id;

        return User::find($userId);
    }

    private function fetchUserPoints(User $user): Collection
    {
        return User::find($this->params['user_id'])
            ->points()
            ->with(['category', 'transactions'])
            ->get();
    }

    private function paginatePoints(Collection $points): Collection
    {
        $page = $this->currentPage();
        $perPage = $this->perPage();

        return $points->forPage($page, $perPage);
    }

    private function formatPointsData($points): array
    {
        if ($points instanceof Collection) {
            $points = $points->first();
        }

        return [
            'id' => $points?->id,
            'balance' => $points?->balance,
            'earned_total' => $points?->earned_total,
            'spent_total' => $points?->spent_total,
            'last_updated' => $points?->updated_at,
        ];
    }

    private function formatPointsCollection(Collection $points): array
    {
        return $points->map(fn($point) => $this->formatPointsData($point))->toArray();
    }

    private function calculateTotalPoints(Collection $points): int
    {
        return $points->sum('balance');
    }

    private function groupPointsByCategory(Collection $points): array
    {
        return $points->load('category')
            ->groupBy('category.name')
            ->map->sum('balance')
            ->toArray();
    }

    private function recentPointsActivity(Collection $points): Collection
    {
        return $points->load(['transactions' => function ($query) {
            $query->where('created_at', '>', now()->subDays(30))
                ->orderByDesc('created_at')
                ->limit(10);
        }])->pluck('transactions')->flatten();
    }

    private function currentPage(): int
    {
        return max((int) ($this->params['page'] ?? 1), 1);
    }

    private function perPage(): int
    {
        return min(max((int) ($this->params['per_page'] ?? 10), 1), 100);
    }

    private function successResult(array $data): array
    {
        return ['success' => true, 'data' => $data, 'errors' => []];
    }

    private function failureResult(string $message): array
    {
        $this->errors[] = $message;

        return ['success' => false, 'data' => null, 'errors' => $this->errors];
    }
}
