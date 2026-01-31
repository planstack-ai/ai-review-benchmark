# Existing Codebase

## Schema

```php
// database/migrations/2024_01_15_000001_create_roles_table.php
Schema::create('roles', function (Blueprint $table) {
    $table->id();
    $table->string('name')->unique();
    $table->string('slug')->unique();
    $table->text('description')->nullable();
    $table->unsignedBigInteger('parent_id')->nullable();
    $table->integer('level')->default(0);
    $table->timestamps();
    
    $table->foreign('parent_id')->references('id')->on('roles')->onDelete('cascade');
    $table->index(['parent_id', 'level']);
});

// database/migrations/2024_01_15_000002_create_permissions_table.php
Schema::create('permissions', function (Blueprint $table) {
    $table->id();
    $table->string('name')->unique();
    $table->string('slug')->unique();
    $table->string('resource');
    $table->string('action');
    $table->timestamps();
    
    $table->index(['resource', 'action']);
});

// database/migrations/2024_01_15_000003_create_role_permissions_table.php
Schema::create('role_permissions', function (Blueprint $table) {
    $table->id();
    $table->foreignId('role_id')->constrained()->onDelete('cascade');
    $table->foreignId('permission_id')->constrained()->onDelete('cascade');
    $table->timestamps();
    
    $table->unique(['role_id', 'permission_id']);
});

// database/migrations/2024_01_15_000004_add_role_id_to_users_table.php
Schema::table('users', function (Blueprint $table) {
    $table->foreignId('role_id')->nullable()->constrained()->onDelete('set null');
});
```

## Models

```php
// app/Models/User.php
class User extends Authenticatable
{
    protected $fillable = [
        'name', 'email', 'password', 'role_id'
    ];

    protected $hidden = [
        'password', 'remember_token',
    ];

    public function role(): BelongsTo
    {
        return $this->belongsTo(Role::class);
    }

    public function scopeWithRole(Builder $query, string $roleSlug): Builder
    {
        return $query->whereHas('role', fn($q) => $q->where('slug', $roleSlug));
    }
}

// app/Models/Role.php
class Role extends Model
{
    protected $fillable = ['name', 'slug', 'description', 'parent_id', 'level'];

    public function users(): HasMany
    {
        return $this->hasMany(User::class);
    }

    public function parent(): BelongsTo
    {
        return $this->belongsTo(Role::class, 'parent_id');
    }

    public function children(): HasMany
    {
        return $this->hasMany(Role::class, 'parent_id');
    }

    public function permissions(): BelongsToMany
    {
        return $this->belongsToMany(Permission::class, 'role_permissions');
    }

    public function scopeWithPermissions(Builder $query): Builder
    {
        return $query->with('permissions');
    }

    public function scopeHierarchical(Builder $query): Builder
    {
        return $query->orderBy('level')->orderBy('name');
    }

    public function getAncestors(): Collection
    {
        $ancestors = collect();
        $current = $this->parent;
        
        while ($current) {
            $ancestors->push($current);
            $current = $current->parent;
        }
        
        return $ancestors;
    }
}

// app/Models/Permission.php
class Permission extends Model
{
    protected $fillable = ['name', 'slug', 'resource', 'action'];

    public function roles(): BelongsToMany
    {
        return $this->belongsToMany(Role::class, 'role_permissions');
    }

    public function scopeForResource(Builder $query, string $resource): Builder
    {
        return $query->where('resource', $resource);
    }

    public function scopeForAction(Builder $query, string $action): Builder
    {
        return $query->where('action', $action);
    }
}
```