# Existing Codebase

## Schema

```php
// Database: carts
Schema::create('carts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->onDelete('cascade');
    $table->timestamps();
});

// Database: cart_items
Schema::create('cart_items', function (Blueprint $table) {
    $table->id();
    $table->foreignId('cart_id')->constrained()->onDelete('cascade');
    $table->foreignId('item_id')->constrained('products');
    $table->integer('quantity')->default(1);
    $table->timestamps();
});

// Database: products (items)
Schema::create('products', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->decimal('price', 10, 2);
    $table->boolean('active')->default(true);
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
    public function cart()
    {
        return $this->hasOne(Cart::class);
    }
}

class Cart extends Model
{
    protected $fillable = ['user_id'];

    public function user()
    {
        return $this->belongsTo(User::class);
    }

    public function cartItems()
    {
        return $this->hasMany(CartItem::class);
    }
}

class CartItem extends Model
{
    protected $fillable = ['cart_id', 'item_id', 'quantity'];

    public function cart()
    {
        return $this->belongsTo(Cart::class);
    }

    public function item()
    {
        return $this->belongsTo(Product::class, 'item_id');
    }
}
```

## Secure Access Pattern

Cart operations should be performed through the user's cart:
```php
$user->cart->cartItems()->create([...]);
```

Not through direct cart ID lookup:
```php
Cart::find($cartId)->cartItems()->create([...]);
```
