# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_create_users_table.php
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('email')->unique();
    $table->timestamp('email_verified_at')->nullable();
    $table->string('password');
    $table->enum('role', ['user', 'admin', 'super_admin'])->default('user');
    $table->boolean('is_internal')->default(false);
    $table->rememberToken();
    $table->timestamps();
});

// database/migrations/2024_01_20_create_reports_table.php
Schema::create('reports', function (Blueprint $table) {
    $table->id();
    $table->string('title');
    $table->text('content');
    $table->enum('status', ['draft', 'pending', 'approved', 'rejected'])->default('draft');
    $table->foreignId('user_id')->constrained()->cascadeOnDelete();
    $table->foreignId('approved_by')->nullable()->constrained('users');
    $table->timestamp('approved_at')->nullable();
    $table->json('metadata')->nullable();
    $table->timestamps();
});
```

## Models

```php
// app/Models/User.php
class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
        'role',
        'is_internal',
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
            'is_internal' => 'boolean',
        ];
    }

    public function reports(): HasMany
    {
        return $this->hasMany(Report::class);
    }

    public function approvedReports(): HasMany
    {
        return $this->hasMany(Report::class, 'approved_by');
    }

    public function scopeAdmins(Builder $query): void
    {
        $query->whereIn('role', ['admin', 'super_admin']);
    }

    public function scopeInternal(Builder $query): void
    {
        $query->where('is_internal', true);
    }

    public function isAdmin(): bool
    {
        return in_array($this->role, ['admin', 'super_admin']);
    }

    public function isSuperAdmin(): bool
    {
        return $this->role === 'super_admin';
    }

    public function isInternalUser(): bool
    {
        return $this->is_internal;
    }

    public function canBypassValidation(): bool
    {
        return $this->isAdmin() && $this->isInternalUser();
    }
}

// app/Models/Report.php
class Report extends Model
{
    use HasFactory;

    protected $fillable = [
        'title',
        'content',
        'status',
        'user_id',
        'approved_by',
        'approved_at',
        'metadata',
    ];

    protected function casts(): array
    {
        return [
            'approved_at' => 'datetime',
            'metadata' => 'array',
        ];
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function approver(): BelongsTo
    {
        return $this->belongsTo(User::class, 'approved_by');
    }

    public function scopePending(Builder $query): void
    {
        $query->where('status', 'pending');
    }

    public function scopeApproved(Builder $query): void
    {
        $query->where('status', 'approved');
    }

    public function isApproved(): bool
    {
        return $this->status === 'approved';
    }

    public function isPending(): bool
    {
        return $this->status === 'pending';
    }

    public function approve(User $approver): void
    {
        $this->update([
            'status' => 'approved',
            'approved_by' => $approver->id,
            'approved_at' => now(),
        ]);
    }
}
```