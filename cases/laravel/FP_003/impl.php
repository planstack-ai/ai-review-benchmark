<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Product;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Database\Eloquent\Builder;

class ProductSearchService
{
    private array $filters;
    private int $perPage;

    public function __construct(array $filters = [], int $perPage = 20)
    {
        $this->filters = $filters;
        $this->perPage = min($perPage, 100);
    }

    public function search(): LengthAwarePaginator
    {
        $query = Product::query()->with('category');

        $this->applyKeywordFilter($query);
        $this->applyCategoryFilter($query);
        $this->applyPriceFilter($query);
        $this->applyAvailabilityFilter($query);
        $this->applySorting($query);

        return $query->paginate($this->perPage);
    }

    private function applyKeywordFilter(Builder $query): void
    {
        if (!empty($this->filters['keyword'])) {
            $keyword = $this->filters['keyword'];
            $query->where(function ($q) use ($keyword) {
                $q->where('name', 'like', "%{$keyword}%")
                  ->orWhere('description', 'like', "%{$keyword}%");
            });
        }
    }

    private function applyCategoryFilter(Builder $query): void
    {
        if (!empty($this->filters['category_id'])) {
            $query->where('category_id', $this->filters['category_id']);
        }
    }

    private function applyPriceFilter(Builder $query): void
    {
        if (!empty($this->filters['min_price'])) {
            $query->where('price', '>=', (float) $this->filters['min_price']);
        }

        if (!empty($this->filters['max_price'])) {
            $query->where('price', '<=', (float) $this->filters['max_price']);
        }
    }

    private function applyAvailabilityFilter(Builder $query): void
    {
        if (isset($this->filters['in_stock']) && $this->filters['in_stock']) {
            $query->where('stock', '>', 0);
        }

        if (isset($this->filters['active'])) {
            $query->where('active', (bool) $this->filters['active']);
        } else {
            $query->where('active', true);
        }
    }

    private function applySorting(Builder $query): void
    {
        $sortField = $this->filters['sort_by'] ?? 'created_at';
        $sortDirection = $this->filters['sort_direction'] ?? 'desc';

        $allowedSortFields = ['name', 'price', 'created_at', 'stock'];

        if (in_array($sortField, $allowedSortFields)) {
            $query->orderBy($sortField, $sortDirection === 'asc' ? 'asc' : 'desc');
        }
    }
}
