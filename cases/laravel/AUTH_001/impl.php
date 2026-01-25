<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Order;
use Illuminate\Support\Facades\Log;

class OrderViewService
{
    private ?int $userId;
    private ?int $orderId;
    private bool $includeItems;
    private bool $includeShipping;
    private ?User $currentUser = null;

    public function __construct(
        ?int $userId,
        ?int $orderId,
        bool $includeItems = false,
        bool $includeShipping = false
    ) {
        $this->userId = $userId;
        $this->orderId = $orderId;
        $this->includeItems = $includeItems;
        $this->includeShipping = $includeShipping;

        if ($userId) {
            $this->currentUser = User::find($userId);
        }
    }

    public function execute(): object
    {
        if (!$this->userId || !$this->orderId) {
            return $this->failureResult('Invalid parameters');
        }

        if (!$this->currentUser) {
            return $this->failureResult('User not found');
        }

        $order = $this->fetchOrder();

        if (!$order) {
            return $this->failureResult('Order not found');
        }

        if (!$this->canAccessOrder($order)) {
            return $this->failureResult('Access denied');
        }

        return $this->buildOrderResponse($order);
    }

    private function fetchOrder(): ?Order
    {
        return Order::find($this->orderId);
    }

    private function canAccessOrder(Order $order): bool
    {
        if (!$order) {
            return false;
        }

        if (!$this->currentUser) {
            return false;
        }

        return $order->user_id === $this->currentUser->id;
    }

    private function buildOrderResponse(Order $order): object
    {
        $responseData = [
            'id' => $order->id,
            'status' => $order->status,
            'total_amount' => $order->total_amount,
            'created_at' => $order->created_at,
            'updated_at' => $order->updated_at,
        ];

        if ($this->includeItems) {
            $responseData['items'] = $this->formatOrderItems($order);
        }

        if ($this->includeShipping) {
            $responseData['shipping_info'] = $this->formatShippingInfo($order);
        }

        return $this->successResult($responseData);
    }

    private function formatOrderItems(Order $order): array
    {
        return $order->orderItems->load('product')->map(function ($item) {
            return [
                'id' => $item->id,
                'product_name' => $item->product->name,
                'quantity' => $item->quantity,
                'unit_price' => $item->unit_price,
                'total_price' => $item->total_price,
            ];
        })->toArray();
    }

    private function formatShippingInfo(Order $order): ?array
    {
        if (!$order->shippingAddress) {
            return null;
        }

        return [
            'address' => $order->shippingAddress->full_address,
            'tracking_number' => $order->tracking_number,
            'estimated_delivery' => $order->estimated_delivery_date,
        ];
    }

    private function successResult(array $data): object
    {
        return (object) ['success' => true, 'data' => $data, 'error' => null];
    }

    private function failureResult(string $errorMessage): object
    {
        return (object) ['success' => false, 'data' => null, 'error' => $errorMessage];
    }
}
