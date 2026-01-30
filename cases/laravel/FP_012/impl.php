<?php

namespace App\Services;

use App\Models\AnalyticsEvent;
use App\Models\UserSession;
use App\Models\PageView;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

class AnalyticsReportService
{
    public function getUserEngagementMetrics(int $userId, Carbon $startDate, Carbon $endDate): array
    {
        $sessionStats = $this->getUserSessionStats($userId, $startDate, $endDate);
        $eventCounts = $this->getUserEventCounts($userId, $startDate, $endDate);
        $pageViewMetrics = $this->getUserPageViewMetrics($userId, $startDate, $endDate);
        
        return [
            'user_id' => $userId,
            'period' => [
                'start' => $startDate->toDateString(),
                'end' => $endDate->toDateString(),
            ],
            'sessions' => $sessionStats,
            'events' => $eventCounts,
            'page_views' => $pageViewMetrics,
            'engagement_score' => $this->calculateEngagementScore($sessionStats, $eventCounts, $pageViewMetrics),
        ];
    }

    public function getTopPerformingPages(Carbon $startDate, Carbon $endDate, int $limit = 10): array
    {
        $sql = "
            SELECT 
                url,
                COUNT(*) as total_views,
                COUNT(DISTINCT user_id) as unique_visitors,
                AVG(time_on_page) as avg_time_on_page,
                COUNT(DISTINCT session_id) as unique_sessions
            FROM page_views 
            WHERE viewed_at BETWEEN ? AND ?
            AND time_on_page IS NOT NULL
            GROUP BY url
            ORDER BY total_views DESC, avg_time_on_page DESC
            LIMIT ?
        ";

        return DB::select($sql, [$startDate, $endDate, $limit]);
    }

    private function getUserSessionStats(int $userId, Carbon $startDate, Carbon $endDate): array
    {
        $sql = "
            SELECT 
                COUNT(*) as total_sessions,
                AVG(TIMESTAMPDIFF(SECOND, started_at, ended_at)) as avg_duration,
                AVG(page_views) as avg_page_views,
                COUNT(CASE WHEN ended_at IS NULL THEN 1 END) as active_sessions
            FROM user_sessions 
            WHERE user_id = ? 
            AND started_at BETWEEN ? AND ?
        ";

        $result = DB::select($sql, [$userId, $startDate, $endDate]);
        return (array) $result[0];
    }

    private function getUserEventCounts(int $userId, Carbon $startDate, Carbon $endDate): array
    {
        $sql = "
            SELECT 
                event_type,
                COUNT(*) as count
            FROM analytics_events 
            WHERE user_id = ? 
            AND occurred_at BETWEEN ? AND ?
            GROUP BY event_type
            ORDER BY count DESC
        ";

        $events = DB::select($sql, [$userId, $startDate, $endDate]);
        
        return array_reduce($events, function ($carry, $event) {
            $carry[$event->event_type] = $event->count;
            return $carry;
        }, []);
    }

    private function getUserPageViewMetrics(int $userId, Carbon $startDate, Carbon $endDate): array
    {
        $sql = "
            SELECT 
                COUNT(*) as total_views,
                COUNT(DISTINCT url) as unique_pages,
                AVG(time_on_page) as avg_time_on_page,
                MAX(time_on_page) as max_time_on_page
            FROM page_views 
            WHERE user_id = ? 
            AND viewed_at BETWEEN ? AND ?
            AND time_on_page IS NOT NULL
        ";

        $result = DB::select($sql, [$userId, $startDate, $endDate]);
        return (array) $result[0];
    }

    private function calculateEngagementScore(array $sessions, array $events, array $pageViews): float
    {
        $sessionScore = ($sessions['total_sessions'] ?? 0) * 10;
        $eventScore = array_sum($events) * 5;
        $pageViewScore = ($pageViews['total_views'] ?? 0) * 2;
        $timeScore = ($pageViews['avg_time_on_page'] ?? 0) / 10;
        
        return round($sessionScore + $eventScore + $pageViewScore + $timeScore, 2);
    }
}