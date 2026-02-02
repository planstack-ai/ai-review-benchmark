# Existing Codebase

## Schema

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('analytics_events', function (Blueprint $table) {
            $table->id();
            $table->string('event_type', 50)->index();
            $table->string('user_id', 36)->nullable()->index();
            $table->string('session_id', 36)->index();
            $table->json('payload');
            $table->timestamp('occurred_at')->index();
            $table->timestamps();
            
            $table->index(['event_type', 'occurred_at']);
        });

        Schema::create('write_queues', function (Blueprint $table) {
            $table->id();
            $table->string('queue_name', 100)->index();
            $table->json('batch_data');
            $table->integer('batch_size')->default(0);
            $table->enum('status', ['pending', 'processing', 'completed', 'failed'])->default('pending');
            $table->timestamp('scheduled_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('write_queues');
        Schema::dropIfExists('analytics_events');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;
use Carbon\Carbon;

class AnalyticsEvent extends Model
{
    protected $fillable = [
        'event_type',
        'user_id', 
        'session_id',
        'payload',
        'occurred_at'
    ];

    protected $casts = [
        'payload' => 'array',
        'occurred_at' => 'datetime'
    ];

    public const BATCH_SIZE = 1000;
    public const MAX_QUEUE_SIZE = 5000;

    public function scopeByType(Builder $query, string $type): Builder
    {
        return $query->where('event_type', $type);
    }

    public function scopeInTimeRange(Builder $query, Carbon $start, Carbon $end): Builder
    {
        return $query->whereBetween('occurred_at', [$start, $end]);
    }

    public function scopePending(Builder $query): Builder
    {
        return $query->whereNull('created_at');
    }
}
```

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class WriteQueue extends Model
{
    protected $fillable = [
        'queue_name',
        'batch_data',
        'batch_size',
        'status',
        'scheduled_at'
    ];

    protected $casts = [
        'batch_data' => 'array',
        'scheduled_at' => 'datetime'
    ];

    public const STATUS_PENDING = 'pending';
    public const STATUS_PROCESSING = 'processing';
    public const STATUS_COMPLETED = 'completed';
    public const STATUS_FAILED = 'failed';

    public function scopeReady(Builder $query): Builder
    {
        return $query->where('status', self::STATUS_PENDING)
                    ->where(function ($q) {
                        $q->whereNull('scheduled_at')
                          ->orWhere('scheduled_at', '<=', now());
                    });
    }

    public function scopeByQueue(Builder $query, string $queueName): Builder
    {
        return $query->where('queue_name', $queueName);
    }

    public function markAsProcessing(): bool
    {
        return $this->update(['status' => self::STATUS_PROCESSING]);
    }

    public function markAsCompleted(): bool
    {
        return $this->update(['status' => self::STATUS_COMPLETED]);
    }
}
```