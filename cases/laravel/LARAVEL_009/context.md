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
        Schema::create('notification_settings', function (Blueprint $table) {
            $table->id();
            $table->string('key')->unique();
            $table->json('channels');
            $table->boolean('enabled')->default(true);
            $table->integer('retry_attempts')->default(3);
            $table->integer('delay_seconds')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('notification_settings');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class NotificationSetting extends Model
{
    protected $fillable = [
        'key',
        'channels',
        'enabled',
        'retry_attempts',
        'delay_seconds',
    ];

    protected $casts = [
        'channels' => 'array',
        'enabled' => 'boolean',
        'retry_attempts' => 'integer',
        'delay_seconds' => 'integer',
    ];

    public function scopeEnabled(Builder $query): Builder
    {
        return $query->where('enabled', true);
    }

    public function scopeForKey(Builder $query, string $key): Builder
    {
        return $query->where('key', $key);
    }

    public function hasChannel(string $channel): bool
    {
        return in_array($channel, $this->channels ?? []);
    }

    public function getMaxRetriesAttribute(): int
    {
        return max(1, $this->retry_attempts);
    }
}
```

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class User extends Model
{
    protected $fillable = [
        'name',
        'email',
        'email_verified_at',
        'password',
        'notification_preferences',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
        'notification_preferences' => 'array',
    ];

    public function notifications(): HasMany
    {
        return $this->hasMany(DatabaseNotification::class);
    }

    public function prefersChannel(string $channel): bool
    {
        $preferences = $this->notification_preferences ?? [];
        return $preferences[$channel] ?? true;
    }
}
```

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class DatabaseNotification extends Model
{
    protected $table = 'notifications';

    protected $fillable = [
        'type',
        'notifiable_type',
        'notifiable_id',
        'data',
        'read_at',
    ];

    protected $casts = [
        'data' => 'array',
        'read_at' => 'datetime',
    ];

    public function notifiable(): BelongsTo
    {
        return $this->morphTo();
    }

    public function markAsRead(): void
    {
        $this->update(['read_at' => now()]);
    }
}
```