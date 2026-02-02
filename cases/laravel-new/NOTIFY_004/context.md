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
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('email')->unique();
            $table->string('first_name');
            $table->string('last_name')->nullable();
            $table->string('phone')->nullable();
            $table->string('company')->nullable();
            $table->timestamp('email_verified_at')->nullable();
            $table->timestamps();
        });

        Schema::create('notification_templates', function (Blueprint $table) {
            $table->id();
            $table->string('name')->unique();
            $table->string('subject');
            $table->text('body');
            $table->json('variables')->nullable();
            $table->boolean('active')->default(true);
            $table->timestamps();
        });

        Schema::create('notifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('template_id')->constrained('notification_templates');
            $table->json('data')->nullable();
            $table->timestamp('sent_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('notifications');
        Schema::dropIfExists('notification_templates');
        Schema::dropIfExists('users');
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

class User extends Model
{
    protected $fillable = [
        'email',
        'first_name',
        'last_name',
        'phone',
        'company',
        'email_verified_at',
    ];

    protected $casts = [
        'email_verified_at' => 'datetime',
    ];

    public function getFullNameAttribute(): ?string
    {
        return trim($this->first_name . ' ' . $this->last_name) ?: null;
    }

    public function getDisplayNameAttribute(): string
    {
        return $this->full_name ?? $this->first_name;
    }

    public function notifications(): HasMany
    {
        return $this->hasMany(Notification::class);
    }
}

class NotificationTemplate extends Model
{
    protected $fillable = [
        'name',
        'subject',
        'body',
        'variables',
        'active',
    ];

    protected $casts = [
        'variables' => 'array',
        'active' => 'boolean',
    ];

    public function scopeActive($query)
    {
        return $query->where('active', true);
    }

    public function notifications(): HasMany
    {
        return $this->hasMany(Notification::class, 'template_id');
    }
}

class Notification extends Model
{
    protected $fillable = [
        'user_id',
        'template_id',
        'data',
        'sent_at',
    ];

    protected $casts = [
        'data' => 'array',
        'sent_at' => 'datetime',
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function template(): BelongsTo
    {
        return $this->belongsTo(NotificationTemplate::class, 'template_id');
    }

    public function scopeSent($query)
    {
        return $query->whereNotNull('sent_at');
    }

    public function scopePending($query)
    {
        return $query->whereNull('sent_at');
    }
}
```