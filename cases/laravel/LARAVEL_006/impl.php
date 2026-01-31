<?php

namespace App\Services;

use App\Models\Order;
use App\Models\Product;
use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Illuminate\Validation\ValidationException;

class OrderCreationService
{
    public function __construct(
        private readonly Product $productModel,
        private readonly User $userModel
    ) {}

    public function createOrderFromRequest(Request $request, User $user): Order
    {
        $this->validateOrderRequest($request);
        
        $product = $this->getValidatedProduct($request->input('product_id'));
        
        $this->validateInventoryAvailability($product, $request->input('quantity'));
        
        return DB::transaction(function () use ($request, $user, $product) {
            $orderData = $this->prepareOrderData($request, $user, $product);
            
            $order = Order::create($request->all());
            
            $this->updateProductInventory($product, $request->input('quantity'));
            
            $this->logOrderCreation($order, $user);
            
            return $order;
        });
    }

    private function validateOrderRequest(Request $request): void
    {
        $request->validate([
            'product_id' => 'required|integer|exists:products,id',
            'quantity' => 'required|integer|min:1|max:100',
            'shipping_address' => 'required|string|max:500',
            'payment_method' => 'required|string|in:credit_card,paypal,bank_transfer',
            'notes' => 'nullable|string|max:1000'
        ]);
    }

    private function getValidatedProduct(int $productId): Product
    {
        $product = $this->productModel->find($productId);
        
        if (!$product || !$product->is_active) {
            throw ValidationException::withMessages([
                'product_id' => 'The selected product is not available.'
            ]);
        }
        
        return $product;
    }

    private function validateInventoryAvailability(Product $product, int $requestedQuantity): void
    {
        if ($product->stock_quantity < $requestedQuantity) {
            throw ValidationException::withMessages([
                'quantity' => 'Insufficient stock available. Only ' . $product->stock_quantity . ' items remaining.'
            ]);
        }
    }

    private function prepareOrderData(Request $request, User $user, Product $product): array
    {
        $quantity = $request->input('quantity');
        $unitPrice = $product->price;
        $totalAmount = $quantity * $unitPrice;
        
        return [
            'user_id' => $user->id,
            'product_id' => $product->id,
            'quantity' => $quantity,
            'unit_price' => $unitPrice,
            'total_amount' => $totalAmount,
            'status' => 'pending',
            'shipping_address' => $request->input('shipping_address'),
            'payment_method' => $request->input('payment_method'),
            'notes' => $request->input('notes'),
            'order_number' => $this->generateOrderNumber()
        ];
    }

    private function updateProductInventory(Product $product, int $quantity): void
    {
        $product->decrement('stock_quantity', $quantity);
        
        if ($product->stock_quantity <= $product->low_stock_threshold) {
            $this->notifyLowStock($product);
        }
    }

    private function generateOrderNumber(): string
    {
        return 'ORD-' . date('Ymd') . '-' . strtoupper(substr(uniqid(), -6));
    }

    private function notifyLowStock(Product $product): void
    {
        Log::warning('Low stock alert', [
            'product_id' => $product->id,
            'product_name' => $product->name,
            'current_stock' => $product->stock_quantity,
            'threshold' => $product->low_stock_threshold
        ]);
    }

    private function logOrderCreation(Order $order, User $user): void
    {
        Log::info('Order created successfully', [
            'order_id' => $order->id,
            'order_number' => $order->order_number,
            'user_id' => $user->id,
            'total_amount' => $order->total_amount
        ]);
    }
}