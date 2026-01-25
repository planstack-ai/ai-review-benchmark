# Existing Codebase

## Schema

```php
// Database: users (with soft deletes)
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email')->unique();
    $table->string('name');
    $table->timestamp('email_verified_at')->nullable();
    $table->string('password');
    $table->softDeletes(); // deleted_at column
    $table->timestamps();
});

// Database: orders
Schema::create('orders', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->string('status')->default('pending');
    $table->decimal('total_amount', 10, 2);
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class User extends Authenticatable
{
    use SoftDeletes;

    protected $fillable = ['name', 'email', 'password'];

    protected $dates = ['deleted_at'];

    public function orders()
    {
        return $this->hasMany(Order::class);
    }
}

class Order extends Model
{
    protected $fillable = ['user_id', 'status', 'total_amount'];

    public function user()
    {
        return $this->belongsTo(User::class)->withTrashed();
    }
}
```

## Privacy Requirements

When generating reports:
- Users who have deleted their accounts (deleted_at IS NOT NULL) should have their data excluded
- This includes their orders and personal information
- Reports should only show data from active users

Correct pattern:
```php
Order::whereHas('user', fn($q) => $q->whereNull('deleted_at'))
```
