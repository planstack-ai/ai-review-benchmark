<?php

declare(strict_types=1);

namespace App\Services;

use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Log;

class RateLimitService
{
    public function __construct(
        private int $maxRequests = 60,
        private int $windowSeconds = 60
    ) {}

    public function attempt(string $key): array
    {
        $cacheKey = "rate_limit:{$key}";

        try {
            $current = Cache::get($cacheKey, ['count' => 0, 'reset_at' => now()->timestamp]);

            // Check if window has expired
            if ($current['reset_at'] <= now()->timestamp) {
                $current = [
                    'count' => 0,
                    'reset_at' => now()->addSeconds($this->windowSeconds)->timestamp,
                ];
            }

            $current['count']++;

            // Store updated count
            $ttl = $current['reset_at'] - now()->timestamp;
            Cache::put($cacheKey, $current, max(1, $ttl));

            $remaining = max(0, $this->maxRequests - $current['count']);
            $allowed = $current['count'] <= $this->maxRequests;

            return [
                'allowed' => $allowed,
                'remaining' => $remaining,
                'reset_at' => $current['reset_at'],
                'limit' => $this->maxRequests,
            ];
        } catch (\Exception $e) {
            // Fail open - allow request if cache is unavailable
            Log::warning("Rate limit cache error: {$e->getMessage()}");

            return [
                'allowed' => true,
                'remaining' => $this->maxRequests,
                'reset_at' => now()->addSeconds($this->windowSeconds)->timestamp,
                'limit' => $this->maxRequests,
            ];
        }
    }

    public function check(string $key): array
    {
        $cacheKey = "rate_limit:{$key}";

        try {
            $current = Cache::get($cacheKey);

            if (!$current || $current['reset_at'] <= now()->timestamp) {
                return [
                    'remaining' => $this->maxRequests,
                    'reset_at' => now()->addSeconds($this->windowSeconds)->timestamp,
                    'limit' => $this->maxRequests,
                ];
            }

            return [
                'remaining' => max(0, $this->maxRequests - $current['count']),
                'reset_at' => $current['reset_at'],
                'limit' => $this->maxRequests,
            ];
        } catch (\Exception $e) {
            Log::warning("Rate limit check error: {$e->getMessage()}");

            return [
                'remaining' => $this->maxRequests,
                'reset_at' => now()->addSeconds($this->windowSeconds)->timestamp,
                'limit' => $this->maxRequests,
            ];
        }
    }

    public function reset(string $key): void
    {
        $cacheKey = "rate_limit:{$key}";
        Cache::forget($cacheKey);
    }

    public function withLimits(int $maxRequests, int $windowSeconds): self
    {
        return new self($maxRequests, $windowSeconds);
    }
}
