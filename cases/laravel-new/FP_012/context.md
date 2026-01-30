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
            $table->foreignId('user_id')->nullable()->index();
            $table->json('properties');
            $table->timestamp('occurred_at')->index();
            $table->timestamps();
            
            $table->index(['event_type', 'occurred_at']);
            $table->index(['user_id', 'occurred_at']);
        });

        Schema::create('user_sessions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->index();
            $table->string('session_id', 100)->unique();
            $table->timestamp('started_at')->index();
            $table->timestamp('ended_at')->nullable()->index();
            $table->integer('page_views')->default(0);
            $table->timestamps();
        });

        Schema::create('page_views', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->nullable()->index();
            $table->foreignId('session_id')->index();
            $table->string('url', 500);
            $table->string('referrer', 500)->nullable();
            $table->timestamp('viewed_at')->index();
            $table->integer('time_on_page')->nullable();
            $table->timestamps();
            
            $table->index(['user_id', 'viewed_at']);
            $table->index(['session_id', 'viewed_at']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('page_views');
        Schema::dropIfExists('user_sessions');
        Schema::dropIfExists('analytics_events');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Carbon\Carbon;

class AnalyticsEvent extends Model
{
    protected $fillable = [
        'event_type',
        'user_id',
        'properties',
        'occurred_at',
    ];

    protected $casts = [
        'properties' => 'array',
        'occurred_at' => 'datetime',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function scopeOfType(Builder $query, string $type): Builder
    {
        return $query->where('event_type', $type);
    }

    public function scopeInDateRange(Builder $query, Carbon $start, Carbon $end): Builder
    {
        return $query->whereBetween('occurred_at', [$start, $end]);
    }

    public function scopeForUser(Builder $query, int $userId): Builder
    {
        return $query->where('user_id', $userId);
    }
}

class UserSession extends Model
{
    protected $fillable = [
        'user_id',
        'session_id',
        'started_at',
        'ended_at',
        'page_views',
    ];

    protected $casts = [
        'started_at' => 'datetime',
        'ended_at' => 'datetime',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function pageViews(): HasMany
    {
        return $this->hasMany(PageView::class, 'session_id');
    }

    public function getDurationAttribute(): ?int
    {
        if (!$this->ended_at) {
            return null;
        }
        
        return $this->ended_at->diffInSeconds($this->started_at);
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->whereNull('ended_at');
    }

    public function scopeCompleted(Builder $query): Builder
    {
        return $query->whereNotNull('ended_at');
    }
}

class PageView extends Model
{
    protected $fillable = [
        'user_id',
        'session_id',
        'url',
        'referrer',
        'viewed_at',
        'time_on_page',
    ];

    protected $casts = [
        'viewed_at' => 'datetime',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function session(): BelongsTo
    {
        return $this->belongsTo(UserSession::class, 'session_id');
    }

    public function scopeForUrl(Builder $query, string $url): Builder
    {
        return $query->where('url', $url);
    }

    public function scopeWithTimeOnPage(Builder $query): Builder
    {
        return $query->whereNotNull('time_on_page');
    }
}
```