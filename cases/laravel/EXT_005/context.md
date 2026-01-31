# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_create_inventory_items_table.php
Schema::create('inventory_items', function (Blueprint $table) {
    $table->id();
    $table->string('sku')->unique();
    $table->string('name');
    $table->integer('local_quantity')->default(0);
    $table->integer('warehouse_quantity')->nullable();
    $table->timestamp('last_warehouse_sync_at')->nullable();
    $table->timestamp('warehouse_sync_requested_at')->nullable();
    $table->enum('sync_status', ['pending', 'syncing', 'synced', 'failed'])->default('pending');
    $table->timestamps();
});

// database/migrations/2024_01_20_create_warehouse_sync_logs_table.php
Schema::create('warehouse_sync_logs', function (Blueprint $table) {
    $table->id();
    $table->foreignId('inventory_item_id')->constrained()->cascadeOnDelete();
    $table->enum('status', ['initiated', 'completed', 'failed']);
    $table->json('response_data')->nullable();
    $table->timestamp('initiated_at');
    $table->timestamp('completed_at')->nullable();
    $table->timestamps();
});
```

## Models

```php
// app/Models/InventoryItem.php
class InventoryItem extends Model
{
    protected $fillable = [
        'sku',
        'name',
        'local_quantity',
        'warehouse_quantity',
        'last_warehouse_sync_at',
        'warehouse_sync_requested_at',
        'sync_status',
    ];

    protected $casts = [
        'last_warehouse_sync_at' => 'datetime',
        'warehouse_sync_requested_at' => 'datetime',
        'sync_status' => SyncStatus::class,
    ];

    public function warehouseSyncLogs(): HasMany
    {
        return $this->hasMany(WarehouseSyncLog::class);
    }

    public function scopePendingWarehouseSync(Builder $query): void
    {
        $query->where('sync_status', SyncStatus::PENDING)
              ->whereNotNull('warehouse_sync_requested_at');
    }

    public function scopeSyncedWithinMinutes(Builder $query, int $minutes): void
    {
        $query->where('last_warehouse_sync_at', '>=', now()->subMinutes($minutes));
    }

    public function scopeStaleWarehouseData(Builder $query, int $minutes): void
    {
        $query->where(function ($q) use ($minutes) {
            $q->whereNull('last_warehouse_sync_at')
              ->orWhere('last_warehouse_sync_at', '<', now()->subMinutes($minutes));
        });
    }

    public function getEffectiveQuantityAttribute(): int
    {
        return $this->warehouse_quantity ?? $this->local_quantity;
    }

    public function isWarehouseDataStale(int $minutes = 30): bool
    {
        return is_null($this->last_warehouse_sync_at) || 
               $this->last_warehouse_sync_at->lt(now()->subMinutes($minutes));
    }
}

// app/Models/WarehouseSyncLog.php
class WarehouseSyncLog extends Model
{
    protected $fillable = [
        'inventory_item_id',
        'status',
        'response_data',
        'initiated_at',
        'completed_at',
    ];

    protected $casts = [
        'response_data' => 'array',
        'initiated_at' => 'datetime',
        'completed_at' => 'datetime',
        'status' => SyncLogStatus::class,
    ];

    public function inventoryItem(): BelongsTo
    {
        return $this->belongsTo(InventoryItem::class);
    }
}

// app/Enums/SyncStatus.php
enum SyncStatus: string
{
    case PENDING = 'pending';
    case SYNCING = 'syncing';
    case SYNCED = 'synced';
    case FAILED = 'failed';
}

// app/Enums/SyncLogStatus.php
enum SyncLogStatus: string
{
    case INITIATED = 'initiated';
    case COMPLETED = 'completed';
    case FAILED = 'failed';
}
```