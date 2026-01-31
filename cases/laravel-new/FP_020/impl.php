<?php

namespace App\Services;

use App\Models\AnalyticsEvent;
use App\Models\WriteQueue;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Carbon\Carbon;

class AsyncWriteService
{
    private array $pendingWrites = [];
    private int $maxBatchSize;
    private int $flushThreshold;

    public function __construct(int $maxBatchSize = 1000, int $flushThreshold = 500)
    {
        $this->maxBatchSize = $maxBatchSize;
        $this->flushThreshold = $flushThreshold;
    }

    public function queueAnalyticsEvent(string $eventType, ?string $userId, string $sessionId, array $payload): void
    {
        $this->pendingWrites[] = [
            'event_type' => $eventType,
            'user_id' => $userId,
            'session_id' => $sessionId,
            'payload' => $payload,
            'occurred_at' => now()
        ];

        if (count($this->pendingWrites) >= $this->flushThreshold) {
            $this->flushPendingWrites();
        }
    }

    public function flushPendingWrites(): void
    {
        if (empty($this->pendingWrites)) {
            return;
        }

        $batches = array_chunk($this->pendingWrites, $this->maxBatchSize);
        
        foreach ($batches as $batch) {
            $this->createWriteQueueBatch('analytics_events', $batch);
        }

        $this->pendingWrites = [];
    }

    public function processQueuedWrites(string $queueName, int $limit = 10): int
    {
        $processedCount = 0;
        
        $queueItems = WriteQueue::ready()
            ->byQueue($queueName)
            ->limit($limit)
            ->get();

        foreach ($queueItems as $queueItem) {
            if ($this->processBatch($queueItem)) {
                $processedCount++;
            }
        }

        return $processedCount;
    }

    private function createWriteQueueBatch(string $queueName, array $batchData): void
    {
        WriteQueue::create([
            'queue_name' => $queueName,
            'batch_data' => $batchData,
            'batch_size' => count($batchData),
            'status' => WriteQueue::STATUS_PENDING,
            'scheduled_at' => now()->addSeconds(rand(1, 30))
        ]);
    }

    private function processBatch(WriteQueue $queueItem): bool
    {
        try {
            $queueItem->markAsProcessing();

            DB::transaction(function () use ($queueItem) {
                if ($queueItem->queue_name === 'analytics_events') {
                    AnalyticsEvent::insert($queueItem->batch_data);
                }
            });

            $queueItem->markAsCompleted();
            return true;

        } catch (\Exception $e) {
            Log::error('Batch processing failed', [
                'queue_id' => $queueItem->id,
                'error' => $e->getMessage()
            ]);
            
            $queueItem->update(['status' => WriteQueue::STATUS_FAILED]);
            return false;
        }
    }

    public function getQueueStats(string $queueName): array
    {
        return [
            'pending' => WriteQueue::byQueue($queueName)->where('status', WriteQueue::STATUS_PENDING)->count(),
            'processing' => WriteQueue::byQueue($queueName)->where('status', WriteQueue::STATUS_PROCESSING)->count(),
            'completed' => WriteQueue::byQueue($queueName)->where('status', WriteQueue::STATUS_COMPLETED)->count(),
            'failed' => WriteQueue::byQueue($queueName)->where('status', WriteQueue::STATUS_FAILED)->count(),
            'pending_writes' => count($this->pendingWrites)
        ];
    }
}