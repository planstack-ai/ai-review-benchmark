# Existing Codebase

## Schema

```php
// Database: users
Schema::create('users', function (Blueprint $table) {
    $table->id();
    $table->string('email')->unique();
    $table->string('name');
    $table->timestamps();
});

// Database: points
Schema::create('points', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained();
    $table->foreignId('category_id')->constrained('point_categories');
    $table->integer('balance')->default(0);
    $table->integer('earned_total')->default(0);
    $table->integer('spent_total')->default(0);
    $table->timestamps();
});

// Database: point_transactions
Schema::create('point_transactions', function (Blueprint $table) {
    $table->id();
    $table->foreignId('points_id')->constrained();
    $table->integer('amount');
    $table->string('type'); // earn, spend
    $table->string('description');
    $table->timestamps();
});
```

## Models

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class User extends Authenticatable
{
    public function points()
    {
        return $this->hasMany(Point::class);
    }
}

class Point extends Model
{
    protected $fillable = ['user_id', 'category_id', 'balance', 'earned_total', 'spent_total'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function category()
    {
        return $this->belongsTo(PointCategory::class);
    }

    public function transactions()
    {
        return $this->hasMany(PointTransaction::class, 'points_id');
    }
}
```

## Security Requirement

Points data is personal financial information. Users should ONLY access their own points:

```php
// Correct: scope through authenticated user
$currentUser->points()->with('category', 'transactions')->get();

// WRONG: allows IDOR vulnerability
User::find($params['user_id'])->points;
```
