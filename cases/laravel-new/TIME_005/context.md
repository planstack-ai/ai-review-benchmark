# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_billing_cycles_table.php
Schema::create('billing_cycles', function (Blueprint $table) {
    $table->id();
    $table->date('start_date');
    $table->date('end_date');
    $table->enum('status', ['pending', 'processing', 'completed', 'failed']);
    $table->decimal('total_amount', 10, 2)->default(0);
    $table->json('processing_metadata')->nullable();
    $table->timestamp('processed_at')->nullable();
    $table->timestamps();
    
    $table->index(['status', 'end_date']);
    $table->unique(['start_date', 'end_date']);
});

// database/migrations/2024_01_15_000002_create_subscriptions_table.php
Schema::create('subscriptions', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->decimal('monthly_amount', 8, 2);
    $table->date('billing_start_date');
    $table->date('next_billing_date');
    $table->enum('status', ['active', 'paused', 'cancelled']);
    $table->timestamps();
    
    $table->index(['status', 'next_billing_date']);
});

// database/migrations/2024_01_15_000003_create_invoices_table.php
Schema::create('invoices', function (Blueprint $table) {
    $table->id();
    $table->foreignId('billing_cycle_id')->constrained();
    $table->foreignId('subscription_id')->constrained();
    $table->decimal('amount', 8, 2);
    $table->date('due_date');
    $table->enum('status', ['draft', 'sent', 'paid', 'overdue']);
    $table->timestamps();
});
```

## Models

```php
// app/Models/BillingCycle.php
class BillingCycle extends Model
{
    protected $fillable = [
        'start_date',
        'end_date', 
        'status',
        'total_amount',
        'processing_metadata',
        'processed_at'
    ];

    protected $casts = [
        'start_date' => 'date',
        'end_date' => 'date',
        'processing_metadata' => 'array',
        'processed_at' => 'datetime'
    ];

    public function invoices(): HasMany
    {
        return $this->hasMany(Invoice::class);
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', 'pending');
    }

    public function scopeForMonth(Builder $query, int $year, int $month): void
    {
        $startDate = Carbon::create($year, $month, 1);
        $endDate = $startDate->copy()->endOfMonth();
        
        $query->where('start_date', $startDate->toDateString())
              ->where('end_date', $endDate->toDateString());
    }

    public function scopeReadyForProcessing(Builder $query): void
    {
        $query->pending()->where('end_date', '<=', now()->toDateString());
    }
}

// app/Models/Subscription.php
class Subscription extends Model
{
    protected $fillable = [
        'user_id',
        'monthly_amount',
        'billing_start_date',
        'next_billing_date',
        'status'
    ];

    protected $casts = [
        'billing_start_date' => 'date',
        'next_billing_date' => 'date'
    ];

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function invoices(): HasMany
    {
        return $this->hasMany(Invoice::class);
    }

    public function scopeActive(Builder $query): void
    {
        $query->where('status', 'active');
    }

    public function scopeDueForBilling(Builder $query, Carbon $date): void
    {
        $query->active()->where('next_billing_date', '<=', $date->toDateString());
    }

    public function calculateNextBillingDate(): Carbon
    {
        return $this->next_billing_date->copy()->addMonth();
    }
}

// app/Models/Invoice.php
class Invoice extends Model
{
    protected $fillable = [
        'billing_cycle_id',
        'subscription_id',
        'amount',
        'due_date',
        'status'
    ];

    protected $casts = [
        'due_date' => 'date'
    ];

    public function billingCycle(): BelongsTo
    {
        return $this->belongsTo(BillingCycle::class);
    }

    public function subscription(): BelongsTo
    {
        return $this->belongsTo(Subscription::class);
    }
}
```