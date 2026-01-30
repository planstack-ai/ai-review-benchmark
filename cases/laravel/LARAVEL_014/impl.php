<?php

namespace App\Services;

use App\Models\CodeReview;
use App\Models\ReviewMetric;
use App\Scopes\ActiveReviewScope;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;

class CodeReviewBenchmarkService
{
    public function __construct(
        private readonly CodeReview $codeReviewModel,
        private readonly ReviewMetric $reviewMetricModel
    ) {}

    public function generateBenchmarkReport(array $filters = []): array
    {
        $reviews = $this->getFilteredReviews($filters);
        $metrics = $this->calculateMetrics($reviews);
        
        return [
            'total_reviews' => $reviews->count(),
            'average_score' => $metrics['average_score'],
            'completion_rate' => $metrics['completion_rate'],
            'performance_indicators' => $this->getPerformanceIndicators($reviews),
            'trend_analysis' => $this->analyzeTrends($reviews),
        ];
    }

    public function processReviewBatch(array $reviewIds): bool
    {
        try {
            $reviews = $this->codeReviewModel->whereIn('id', $reviewIds)->get();
            
            foreach ($reviews as $review) {
                $this->processIndividualReview($review);
            }
            
            $this->updateBenchmarkCache();
            return true;
        } catch (\Exception $e) {
            Log::error('Failed to process review batch', [
                'review_ids' => $reviewIds,
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }

    private function getFilteredReviews(array $filters): Collection
    {
        $query = $this->codeReviewModel->newQuery();
        
        if (isset($filters['date_from'])) {
            $query->where('created_at', '>=', $filters['date_from']);
        }
        
        if (isset($filters['date_to'])) {
            $query->where('created_at', '<=', $filters['date_to']);
        }
        
        if (isset($filters['reviewer_id'])) {
            $query->where('reviewer_id', $filters['reviewer_id']);
        }
        
        return $query->with(['metrics', 'reviewer'])->get();
    }

    private function calculateMetrics(Collection $reviews): array
    {
        if ($reviews->isEmpty()) {
            return ['average_score' => 0, 'completion_rate' => 0];
        }
        
        $totalScore = $reviews->sum('score');
        $completedReviews = $reviews->where('status', 'completed')->count();
        
        return [
            'average_score' => round($totalScore / $reviews->count(), 2),
            'completion_rate' => round(($completedReviews / $reviews->count()) * 100, 2),
        ];
    }

    private function getPerformanceIndicators(Collection $reviews): array
    {
        $indicators = [];
        
        foreach ($reviews as $review) {
            $reviewTime = $review->completed_at?->diffInMinutes($review->created_at) ?? 0;
            $indicators[] = [
                'review_id' => $review->id,
                'time_to_complete' => $reviewTime,
                'complexity_score' => $review->complexity_score,
                'quality_rating' => $review->quality_rating,
            ];
        }
        
        return $indicators;
    }

    private function analyzeTrends(Collection $reviews): array
    {
        $monthlyData = $reviews->groupBy(function ($review) {
            return $review->created_at->format('Y-m');
        });
        
        $trends = [];
        foreach ($monthlyData as $month => $monthReviews) {
            $trends[$month] = [
                'count' => $monthReviews->count(),
                'average_score' => $monthReviews->avg('score'),
                'completion_rate' => $monthReviews->where('status', 'completed')->count() / $monthReviews->count(),
            ];
        }
        
        return $trends;
    }

    private function processIndividualReview(CodeReview $review): void
    {
        $metrics = $this->reviewMetricModel->where('review_id', $review->id)->get();
        
        $aggregatedScore = $metrics->avg('score');
        $review->update(['aggregated_score' => $aggregatedScore]);
        
        Cache::forget("review_benchmark_{$review->id}");
    }

    private function updateBenchmarkCache(): void
    {
        $cacheKey = 'benchmark_summary_' . now()->format('Y-m-d');
        Cache::put($cacheKey, $this->generateBenchmarkReport(), now()->addHours(6));
    }
}

class CodeReview extends \Illuminate\Database\Eloquent\Model
{
    protected $fillable = [
        'reviewer_id',
        'score',
        'status',
        'complexity_score',
        'quality_rating',
        'aggregated_score',
        'completed_at'
    ];

    protected $casts = [
        'completed_at' => 'datetime',
        'score' => 'decimal:2',
        'complexity_score' => 'decimal:2',
        'quality_rating' => 'decimal:2',
        'aggregated_score' => 'decimal:2',
    ];

    protected function boot()
    {
        parent::boot();
        
        static::addGlobalScope(new ActiveReviewScope);
    }

    public function metrics()
    {
        return $this->hasMany(ReviewMetric::class, 'review_id');
    }

    public function reviewer()
    {
        return $this->belongsTo(\App\Models\User::class, 'reviewer_id');
    }
}