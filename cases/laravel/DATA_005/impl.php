<?php

namespace App\Services;

use App\Models\Order;
use App\Models\OrderItem;
use App\Models\Product;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\DB;

class OrderProcessingService
{
    public function __construct(
        private readonly Order $orderModel,
        private readonly OrderItem $orderItemModel,
        private readonly Product $productModel
    ) {}

    public function createOrder(array $orderData, array $items): Order
    {
        return DB::transaction(function () use ($orderData, $items) {
            $order = $this->orderModel->create([
                'user_id' => $orderData['user_id'],
                'status' => 'pending',
                'total_amount' => 0,
                'order_date' => now(),
                'shipping_address' => $orderData['shipping_address'],
                'billing_address' => $orderData['billing_address'] ?? $orderData['shipping_address'],
            ]);

            $totalAmount = $this->processOrderItems($order, $items);
            
            $order->update(['total_amount' => $totalAmount]);

            return $order->fresh();
        });
    }

    public function getOrderWithItems(int $orderId): ?Order
    {
        return $this->orderModel
            ->with(['orderItems.product', 'user'])
            ->find($orderId);
    }

    public function updateOrderStatus(int $orderId, string $status): bool
    {
        $order = $this->orderModel->find($orderId);
        
        if (!$order) {
            return false;
        }

        return $order->update(['status' => $status]);
    }

    public function calculateOrderTotal(Order $order): float
    {
        return $order->orderItems->sum(function ($item) {
            return $item->quantity * $item->unit_price;
        });
    }

    private function processOrderItems(Order $order, array $items): float
    {
        $totalAmount = 0;

        foreach ($items as $itemData) {
            $product = $this->validateAndGetProduct($itemData['product_id'], $itemData['quantity']);
            
            $orderItem = $this->createOrderItem($order, $product, $itemData);
            
            $totalAmount += $orderItem->quantity * $orderItem->unit_price;
        }

        return $totalAmount;
    }

    private function validateAndGetProduct(int $productId, int $quantity): Product
    {
        $product = $this->productModel->find($productId);

        if (!$product) {
            throw new \InvalidArgumentException("Product with ID {$productId} not found");
        }

        if (!$product->is_active) {
            throw new \InvalidArgumentException("Product {$product->name} is not available");
        }

        if ($product->stock_quantity < $quantity) {
            throw new \InvalidArgumentException("Insufficient stock for product {$product->name}");
        }

        return $product;
    }

    private function createOrderItem(Order $order, Product $product, array $itemData): OrderItem
    {
        $orderItem = $this->orderItemModel->create([
            'order_id' => $order->id,
            'product_id' => $product->id,
            'quantity' => $itemData['quantity'],
            'unit_price' => $product->price,
        ]);

        $this->updateProductStock($product, $itemData['quantity']);

        return $orderItem;
    }

    private function updateProductStock(Product $product, int $quantity): void
    {
        $product->decrement('stock_quantity', $quantity);
    }
}