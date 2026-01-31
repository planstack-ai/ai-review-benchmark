<?php

namespace App\Services;

use App\Models\Order;
use App\Models\OrderItem;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use InvalidArgumentException;

class OrderUpdateService
{
    public function __construct(
        private readonly Order $orderModel,
        private readonly OrderItem $orderItemModel
    ) {}

    public function updateOrder(int $orderId, array $orderData): Order
    {
        $order = $this->findOrderById($orderId);
        
        $this->validateOrderData($orderData);
        
        return DB::transaction(function () use ($order, $orderData) {
            $updatedOrder = $this->performOrderUpdate($order, $orderData);
            
            if (isset($orderData['items'])) {
                $this->updateOrderItems($updatedOrder, $orderData['items']);
            }
            
            $this->recalculateOrderTotals($updatedOrder);
            
            Log::info('Order updated successfully', [
                'order_id' => $updatedOrder->id,
                'updated_by' => auth()->id()
            ]);
            
            return $updatedOrder->fresh();
        });
    }

    private function findOrderById(int $orderId): Order
    {
        $order = $this->orderModel->find($orderId);
        
        if (!$order) {
            throw new ModelNotFoundException("Order with ID {$orderId} not found");
        }
        
        return $order;
    }

    private function validateOrderData(array $orderData): void
    {
        $allowedFields = ['status', 'shipping_address', 'billing_address', 'notes', 'items'];
        
        foreach (array_keys($orderData) as $field) {
            if (!in_array($field, $allowedFields)) {
                throw new InvalidArgumentException("Field '{$field}' is not allowed for update");
            }
        }
        
        if (isset($orderData['status']) && !in_array($orderData['status'], ['pending', 'processing', 'shipped', 'delivered', 'cancelled'])) {
            throw new InvalidArgumentException('Invalid order status provided');
        }
    }

    private function performOrderUpdate(Order $order, array $orderData): Order
    {
        $updateData = array_intersect_key($orderData, array_flip(['status', 'shipping_address', 'billing_address', 'notes']));
        
        if (!empty($updateData)) {
            $order->update($updateData);
        }
        
        return $order;
    }

    private function updateOrderItems(Order $order, array $itemsData): void
    {
        foreach ($itemsData as $itemData) {
            if (isset($itemData['id'])) {
                $this->updateExistingItem($itemData);
            } else {
                $this->createNewItem($order, $itemData);
            }
        }
    }

    private function updateExistingItem(array $itemData): void
    {
        $item = $this->orderItemModel->findOrFail($itemData['id']);
        
        $updateFields = array_intersect_key($itemData, array_flip(['quantity', 'price', 'notes']));
        
        if (!empty($updateFields)) {
            $item->update($updateFields);
        }
    }

    private function createNewItem(Order $order, array $itemData): void
    {
        $order->items()->create([
            'product_id' => $itemData['product_id'],
            'quantity' => $itemData['quantity'],
            'price' => $itemData['price'],
            'notes' => $itemData['notes'] ?? null
        ]);
    }

    private function recalculateOrderTotals(Order $order): void
    {
        $subtotal = $order->items()->sum(DB::raw('quantity * price'));
        $tax = $subtotal * 0.08;
        $total = $subtotal + $tax;
        
        $order->update([
            'subtotal' => $subtotal,
            'tax_amount' => $tax,
            'total_amount' => $total
        ]);
    }
}