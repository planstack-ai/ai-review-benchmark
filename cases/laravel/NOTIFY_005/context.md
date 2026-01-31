# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_users_table.php
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email')->unique();
    $table->timestamp('email_verified_at')->nullable();
    $table->string('password');
    $table->enum('role', ['admin', 'manager', 'employee'])->default('employee');
    $table->boolean('is_active')->default(true);
    $table->timestamps();
});

// database/migrations/2024_01_15_000002_create_notifications_table.php
Schema::create('notifications', function (Blueprint $table) {
    $table->id();
    $table->string('type');
    $table->morphs('notifiable');
    $table->text('data');
    $table->timestamp('read_at')->nullable();
    $table->timestamps();
});

// database/migrations/2024_01_15_000003_create_orders_table.php
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('customer_id')->constrained('users');
    $table->foreignId('assigned_manager_id')->nullable()->constrained('users');
    $table->string('order_number')->unique();
    $table->enum('status', ['pending', 'processing', 'completed', 'cancelled']);
    $table->decimal('total_amount', 10, 2);
    $table->timestamps();
});
```

## Models

```php
// app/Models/User.php
class User extends Authenticatable implements CanResetPassword
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
        'role',
        'is_active',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
            'is_active' => 'boolean',
        ];
    }

    public function scopeActive(Builder $query): void
    {
        $query->where('is_active', true);
    }

    public function scopeManagers(Builder $query): void
    {
        $query->where('role', 'manager');
    }

    public function scopeCustomers(Builder $query): void
    {
        $query->where('role', 'employee');
    }

    public function customerOrders(): HasMany
    {
        return $this->hasMany(Order::class, 'customer_id');
    }

    public function managedOrders(): HasMany
    {
        return $this->hasMany(Order::class, 'assigned_manager_id');
    }

    public function getDisplayNameAttribute(): string
    {
        return $this->name;
    }

    public function isManager(): bool
    {
        return $this->role === 'manager';
    }

    public function isCustomer(): bool
    {
        return $this->role === 'employee';
    }
}

// app/Models/Order.php
class Order extends Model
{
    use HasFactory;

    protected $fillable = [
        'customer_id',
        'assigned_manager_id',
        'order_number',
        'status',
        'total_amount',
    ];

    protected function casts(): array
    {
        return [
            'total_amount' => 'decimal:2',
        ];
    }

    public function customer(): BelongsTo
    {
        return $this->belongsTo(User::class, 'customer_id');
    }

    public function assignedManager(): BelongsTo
    {
        return $this->belongsTo(User::class, 'assigned_manager_id');
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', 'pending');
    }

    public function scopeProcessing(Builder $query): void
    {
        $query->where('status', 'processing');
    }

    public function getFormattedTotalAttribute(): string
    {
        return '$' . number_format($this->total_amount, 2);
    }

    public function isPending(): bool
    {
        return $this->status === 'pending';
    }

    public function isProcessing(): bool
    {
        return $this->status === 'processing';
    }
}
```