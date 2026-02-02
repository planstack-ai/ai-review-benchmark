<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class Product extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'sku',
        'price',
        'cost',
        'currency',
        'is_active',
    ];

    protected $casts = [
        'price' => 'integer',
        'cost' => 'integer',
        'is_active' => 'boolean',
    ];

    public function scopeActive(Builder $query): void
    {
        $query->where('is_active', true);
    }

    public function scopeInCurrency(Builder $query, string $currency): void
    {
        $query->where('currency', $currency);
    }

    /**
     * Get the price in dollars for display.
     * BUG: Accessing $this->price triggers this accessor again, causing infinite recursion.
     */
    public function getPriceAttribute(): float
    {
        return $this->price / 100;
    }

    /**
     * Set the price from dollars to cents for storage.
     */
    public function setPriceAttribute(float $value): void
    {
        $this->attributes['price'] = (int) round($value * 100);
    }

    /**
     * Get the cost in dollars for display.
     */
    public function getCostAttribute(): ?float
    {
        return $this->cost ? $this->attributes['cost'] / 100 : null;
    }

    /**
     * Set the cost from dollars to cents for storage.
     */
    public function setCostAttribute(?float $value): void
    {
        $this->attributes['cost'] = $value ? (int) round($value * 100) : null;
    }

    /**
     * Calculate profit margin percentage.
     */
    public function getMarginAttribute(): ?float
    {
        if (!$this->attributes['cost'] || $this->attributes['price'] <= 0) {
            return null;
        }

        return (($this->attributes['price'] - $this->attributes['cost']) / $this->attributes['price']) * 100;
    }

    /**
     * Format the price for display with currency symbol.
     */
    public function getFormattedPriceAttribute(): string
    {
        $amount = $this->price;

        return match ($this->currency) {
            'USD' => '$' . number_format($amount, 2),
            'EUR' => '€' . number_format($amount, 2, ',', '.'),
            'GBP' => '£' . number_format($amount, 2),
            default => $this->currency . ' ' . number_format($amount, 2),
        };
    }

    /**
     * Check if product is on sale.
     */
    public function isOnSale(): bool
    {
        return $this->sale_price !== null && $this->sale_price < $this->price;
    }
}
