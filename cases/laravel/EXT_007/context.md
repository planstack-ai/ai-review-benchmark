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
        Schema::create('external_api_logs', function (Blueprint $table) {
            $table->id();
            $table->string('service_name');
            $table->string('endpoint');
            $table->string('method');
            $table->json('request_data')->nullable();
            $table->json('response_data')->nullable();
            $table->integer('status_code')->nullable();
            $table->text('error_message')->nullable();
            $table->boolean('is_valid_response')->default(false);
            $table->timestamp('requested_at');
            $table->timestamps();
            
            $table->index(['service_name', 'endpoint']);
            $table->index('is_valid_response');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('external_api_logs');
    }
};
```

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('api_response_schemas', function (Blueprint $table) {
            $table->id();
            $table->string('service_name');
            $table->string('endpoint');
            $table->string('method');
            $table->json('required_fields');
            $table->json('field_types');
            $table->json('validation_rules')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            
            $table->unique(['service_name', 'endpoint', 'method']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('api_response_schemas');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Builder;

class ExternalApiLog extends Model
{
    protected $fillable = [
        'service_name',
        'endpoint',
        'method',
        'request_data',
        'response_data',
        'status_code',
        'error_message',
        'is_valid_response',
        'requested_at',
    ];

    protected $casts = [
        'request_data' => 'array',
        'response_data' => 'array',
        'is_valid_response' => 'boolean',
        'requested_at' => 'datetime',
    ];

    public function schema(): BelongsTo
    {
        return $this->belongsTo(ApiResponseSchema::class, ['service_name', 'endpoint', 'method'], ['service_name', 'endpoint', 'method']);
    }

    public function scopeValid(Builder $query): Builder
    {
        return $query->where('is_valid_response', true);
    }

    public function scopeInvalid(Builder $query): Builder
    {
        return $query->where('is_valid_response', false);
    }

    public function scopeForService(Builder $query, string $serviceName): Builder
    {
        return $query->where('service_name', $serviceName);
    }

    public function scopeSuccessful(Builder $query): Builder
    {
        return $query->whereBetween('status_code', [200, 299]);
    }
}
```

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Builder;

class ApiResponseSchema extends Model
{
    protected $fillable = [
        'service_name',
        'endpoint',
        'method',
        'required_fields',
        'field_types',
        'validation_rules',
        'is_active',
    ];

    protected $casts = [
        'required_fields' => 'array',
        'field_types' => 'array',
        'validation_rules' => 'array',
        'is_active' => 'boolean',
    ];

    public function logs(): HasMany
    {
        return $this->hasMany(ExternalApiLog::class, ['service_name', 'endpoint', 'method'], ['service_name', 'endpoint', 'method']);
    }

    public function scopeActive(Builder $query): Builder
    {
        return $query->where('is_active', true);
    }

    public function scopeForEndpoint(Builder $query, string $serviceName, string $endpoint, string $method): Builder
    {
        return $query->where([
            'service_name' => $serviceName,
            'endpoint' => $endpoint,
            'method' => $method,
        ]);
    }

    public function getValidationRulesAttribute(?array $value): array
    {
        return $value ?? [];
    }
}
```