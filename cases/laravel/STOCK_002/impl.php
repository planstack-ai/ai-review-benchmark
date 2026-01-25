<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Product;
use Illuminate\Support\Facades\Log;

class StockUpdateService
{
    private int $productId;
    private int $quantity;
    private ?Product $product = null;

    public function __construct(int $productId, int $quantity = 1)
    {
        $this->productId = $productId;
        $this->quantity = $quantity;
    }

    public function execute(): array
    {
        $this->validateInputs();
        $this->loadProduct();

        return $this->processStockUpdate();
    }

    private function validateInputs(): void
    {
        if ($this->quantity <= 0) {
            throw new \InvalidArgumentException('Quantity must be positive');
        }
    }

    private function loadProduct(): void
    {
        $this->product = Product::find($this->productId);

        if (!$this->product) {
            throw new \Exception("Product with ID {$this->productId} not found");
        }
    }

    private function processStockUpdate(): array
    {
        try {
            $this->checkStockAvailability();
            $this->updateStockLevel();
            $this->logStockChange();

            return [
                'success' => true,
                'product' => $this->product,
                'remaining_stock' => $this->product->stock,
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => $e->getMessage(),
                'product' => $this->product,
            ];
        }
    }

    private function checkStockAvailability(): void
    {
        if ($this->product->stock < $this->quantity) {
            throw new \Exception(
                "Insufficient stock. Available: {$this->product->stock}, Requested: {$this->quantity}"
            );
        }
    }

    private function updateStockLevel(): void
    {
        $newStockLevel = $this->product->stock - $this->quantity;
        $this->product->update(['stock' => $newStockLevel]);
    }

    private function logStockChange(): void
    {
        $oldStock = $this->product->stock + $this->quantity;
        Log::info("Stock updated for product {$this->product->id}: {$oldStock} -> {$this->product->stock}");
    }
}
