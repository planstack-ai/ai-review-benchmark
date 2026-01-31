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
        Schema::create('events', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->datetime('start_date');
            $table->datetime('end_date');
            $table->string('status')->default('active');
            $table->timestamps();
            
            $table->index(['start_date', 'end_date']);
            $table->index('status');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('events');
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
        Schema::create('reports', function (Blueprint $table) {
            $table->id();
            $table->string('title');
            $table->integer('year');
            $table->integer('quarter')->nullable();
            $table->integer('month')->nullable();
            $table->json('data');
            $table->datetime('generated_at');
            $table->timestamps();
            
            $table->index(['year', 'quarter', 'month']);
            $table->index('generated_at');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('reports');
    }
};
```

## Models

```php
<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Casts\Attribute;

class Event extends Model
{
    protected $fillable = [
        'name',
        'start_date',
        'end_date',
        'status',
    ];

    protected $casts = [
        'start_date' => 'datetime',
        'end_date' => 'datetime',
    ];

    public function scopeActive(Builder $query): void
    {
        $query->where('status', 'active');
    }

    public function scopeInDateRange(Builder $query, Carbon $startDate, Carbon $endDate): void
    {
        $query->where(function ($q) use ($startDate, $endDate) {
            $q->whereBetween('start_date', [$startDate, $endDate])
              ->orWhereBetween('end_date', [$startDate, $endDate])
              ->orWhere(function ($subQ) use ($startDate, $endDate) {
                  $subQ->where('start_date', '<=', $startDate)
                       ->where('end_date', '>=', $endDate);
              });
        });
    }

    public function scopeSpansYears(Builder $query): void
    {
        $query->whereRaw('YEAR(start_date) != YEAR(end_date)');
    }

    protected function duration(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->start_date->diffInDays($this->end_date)
        );
    }

    protected function isMultiYear(): Attribute
    {
        return Attribute::make(
            get: fn () => $this->start_date->year !== $this->end_date->year
        );
    }
}
```

```php
<?php

namespace App\Models;

use Carbon\Carbon;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

class Report extends Model
{
    protected $fillable = [
        'title',
        'year',
        'quarter',
        'month',
        'data',
        'generated_at',
    ];

    protected $casts = [
        'data' => 'array',
        'generated_at' => 'datetime',
    ];

    public function scopeForYear(Builder $query, int $year): void
    {
        $query->where('year', $year);
    }

    public function scopeForQuarter(Builder $query, int $year, int $quarter): void
    {
        $query->where('year', $year)->where('quarter', $quarter);
    }

    public function scopeForMonth(Builder $query, int $year, int $month): void
    {
        $query->where('year', $year)->where('month', $month);
    }

    public function scopeForDateRange(Builder $query, Carbon $startDate, Carbon $endDate): void
    {
        $startYear = $startDate->year;
        $endYear = $endDate->year;
        
        if ($startYear === $endYear) {
            $query->where('year', $startYear);
        } else {
            $query->whereBetween('year', [$startYear, $endYear]);
        }
    }

    public static function getYearBoundaries(Carbon $date): array
    {
        return [
            'start' => $date->copy()->startOfYear(),
            'end' => $date->copy()->endOfYear(),
        ];
    }
}
```