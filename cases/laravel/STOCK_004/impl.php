<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\InventoryAdjustment;
use App\Models\Product;
use App\Models\User;
use Illuminate\Support\Facades\DB;

class InventoryAdjustmentService
{
    private const VALID_REASON_CODES = ['damaged', 'audit', 'correction', 'shrinkage'];
    private const APPROVAL_THRESHOLD = 100;

    public function createAdjustment(
        int $productId,
        int $quantityChange,
        string $reasonCode,
        ?string $notes,
        User $user
    ): array {
        if (!in_array($reasonCode, self::VALID_REASON_CODES)) {
            return [
                'success' => false,
                'message' => 'Invalid reason code',
            ];
        }

        $product = Product::findOrFail($productId);

        // BUG: Only checks if result would be negative, but doesn't prevent it
        // The check happens but adjustment proceeds anyway
        $newQuantity = $product->stock_quantity + $quantityChange;
        if ($newQuantity < 0) {
            // Warning logged but not returned as error
            \Log::warning("Adjustment would result in negative stock for product {$productId}");
        }

        $needsApproval = abs($quantityChange) > self::APPROVAL_THRESHOLD;

        $adjustment = InventoryAdjustment::create([
            'product_id' => $productId,
            'user_id' => $user->id,
            'quantity_change' => $quantityChange,
            'stock_before' => $product->stock_quantity,
            'stock_after' => $newQuantity,
            'reason_code' => $reasonCode,
            'notes' => $notes,
            'status' => $needsApproval ? 'pending' : 'approved',
        ]);

        if (!$needsApproval) {
            $this->applyAdjustment($adjustment);
        }

        return [
            'success' => true,
            'adjustment' => $adjustment,
            'needs_approval' => $needsApproval,
        ];
    }

    public function approveAdjustment(int $adjustmentId, User $approver): array
    {
        $adjustment = InventoryAdjustment::findOrFail($adjustmentId);

        if ($adjustment->status !== 'pending') {
            return [
                'success' => false,
                'message' => 'Adjustment is not pending',
            ];
        }

        $adjustment->update(['status' => 'approved']);
        $this->applyAdjustment($adjustment);

        return [
            'success' => true,
            'adjustment' => $adjustment->fresh(),
        ];
    }

    private function applyAdjustment(InventoryAdjustment $adjustment): void
    {
        DB::transaction(function () use ($adjustment) {
            $product = Product::lockForUpdate()->findOrFail($adjustment->product_id);

            // BUG: Applies adjustment without re-checking negative stock constraint
            $product->stock_quantity += $adjustment->quantity_change;
            $product->save();

            $adjustment->update(['status' => 'completed']);
        });
    }
}
