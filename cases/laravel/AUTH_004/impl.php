<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Product;
use App\Models\PriceHistory;
use App\Jobs\ProductPriceChangeNotificationJob;
use Illuminate\Support\Facades\DB;

class ProductPriceUpdateService
{
    private int $productId;
    private float $newPrice;
    private User $currentUser;
    private string $reason;
    private array $errors = [];
    private array $priceHistory = [];

    public function __construct(int $productId, float $newPrice, User $currentUser, string $reason)
    {
        $this->productId = $productId;
        $this->newPrice = $newPrice;
        $this->currentUser = $currentUser;
        $this->reason = $reason;
    }

    public function execute(): array
    {
        if (!$this->validate()) {
            return $this->failureResult();
        }

        if (!$this->productExists()) {
            return $this->failureResult();
        }

        if (!$this->priceChanged()) {
            return $this->failureResult();
        }

        try {
            DB::transaction(function () {
                $this->updateProductPrice();
                $this->createPriceHistoryRecord();
                $this->notifyStakeholders();
            });

            return $this->successResult();
        } catch (\Exception $e) {
            $this->errors[] = "Price update failed: {$e->getMessage()}";
            return $this->failureResult();
        }
    }

    private function validate(): bool
    {
        if ($this->newPrice <= 0) {
            $this->errors[] = 'New price must be greater than 0';
            return false;
        }

        if (strlen($this->reason) < 10 || strlen($this->reason) > 500) {
            $this->errors[] = 'Reason must be between 10 and 500 characters';
            return false;
        }

        return true;
    }

    private function productExists(): bool
    {
        if ($this->getProduct()) {
            return true;
        }

        $this->errors[] = 'Product not found';
        return false;
    }

    private function priceChanged(): bool
    {
        if ($this->newPrice !== $this->getProduct()->price) {
            return true;
        }

        $this->errors[] = 'New price must be different from current price';
        return false;
    }

    private function updateProductPrice(): void
    {
        $product = $this->getProduct();
        $product->update([
            'price' => $this->newPrice,
            'price_updated_at' => now(),
            'price_updated_by' => $this->currentUser->id,
        ]);
    }

    private function createPriceHistoryRecord(): void
    {
        $product = $this->getProduct();

        $this->priceHistory[] = PriceHistory::create([
            'product_id' => $product->id,
            'old_price' => $product->getOriginal('price'),
            'new_price' => $this->newPrice,
            'changed_by' => $this->currentUser->id,
            'reason' => $this->reason,
            'changed_at' => now(),
        ]);
    }

    private function notifyStakeholders(): void
    {
        if (!$this->significantPriceChange()) {
            return;
        }

        $product = $this->getProduct();

        ProductPriceChangeNotificationJob::dispatch(
            $product->id,
            $product->getOriginal('price'),
            $this->newPrice,
            $this->currentUser->id
        );
    }

    private function significantPriceChange(): bool
    {
        $product = $this->getProduct();
        $oldPrice = $product->getOriginal('price');

        if (!$oldPrice) {
            return false;
        }

        $percentageChange = abs(($this->newPrice - $oldPrice) / $oldPrice * 100);

        return $percentageChange >= 10.0;
    }

    private function getProduct(): ?Product
    {
        static $product = null;

        if ($product === null) {
            $product = Product::find($this->productId);
        }

        return $product;
    }

    private function successResult(): array
    {
        $product = $this->getProduct()->fresh();

        return [
            'success' => true,
            'product' => $product,
            'price_history' => end($this->priceHistory),
            'message' => "Price updated successfully from {$product->getOriginal('price')} to {$this->newPrice}",
        ];
    }

    private function failureResult(): array
    {
        return [
            'success' => false,
            'errors' => $this->errors,
            'product' => $this->getProduct(),
        ];
    }
}
