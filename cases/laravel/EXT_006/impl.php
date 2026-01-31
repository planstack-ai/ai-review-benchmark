<?php

namespace App\Services;

use App\Models\Order;
use App\Models\ShippingLabel;
use App\Exceptions\ShippingException;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;

class ShippingService
{
    public function __construct(
        private readonly string $shippingApiUrl,
        private readonly string $shippingApiKey,
        private readonly int $timeoutSeconds = 30
    ) {}

    public function processOrderShipment(Order $order): bool
    {
        if ($order->status !== 'ready_to_ship') {
            throw new ShippingException('Order is not ready for shipment');
        }

        DB::beginTransaction();

        try {
            $shippingData = $this->prepareShippingData($order);
            $response = $this->sendShippingRequest($shippingData);
            
            $this->updateOrderStatus($order, $response);
            $this->createShippingLabel($order, $response);
            
            DB::commit();
            
            Log::info('Order shipped successfully', [
                'order_id' => $order->id,
                'tracking_number' => $response['tracking_number'] ?? null
            ]);
            
            return true;
        } catch (\Exception $e) {
            DB::rollBack();
            Log::error('Shipping process failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage()
            ]);
            throw $e;
        }
    }

    private function prepareShippingData(Order $order): array
    {
        return [
            'order_id' => $order->id,
            'recipient' => [
                'name' => $order->shipping_name,
                'address' => $order->shipping_address,
                'city' => $order->shipping_city,
                'state' => $order->shipping_state,
                'zip' => $order->shipping_zip,
                'country' => $order->shipping_country ?? 'US'
            ],
            'package' => [
                'weight' => $this->calculateTotalWeight($order),
                'dimensions' => $this->getPackageDimensions($order),
                'value' => $order->total_amount
            ],
            'service_type' => $order->shipping_method ?? 'standard'
        ];
    }

    private function sendShippingRequest(array $shippingData): array
    {
        $response = Http::timeout($this->timeoutSeconds)
            ->withHeaders([
                'Authorization' => 'Bearer ' . $this->shippingApiKey,
                'Content-Type' => 'application/json'
            ])
            ->post($this->shippingApiUrl . '/shipments', $shippingData);

        return $response->json();
    }

    private function updateOrderStatus(Order $order, array $response): void
    {
        $order->update([
            'status' => 'shipped',
            'shipped_at' => now(),
            'tracking_number' => $response['tracking_number'] ?? null
        ]);
    }

    private function createShippingLabel(Order $order, array $response): void
    {
        if (isset($response['label_url'])) {
            ShippingLabel::create([
                'order_id' => $order->id,
                'label_url' => $response['label_url'],
                'tracking_number' => $response['tracking_number'],
                'carrier' => $response['carrier'] ?? 'unknown'
            ]);
        }
    }

    private function calculateTotalWeight(Order $order): float
    {
        return $order->items->sum(function ($item) {
            return $item->quantity * ($item->product->weight ?? 1.0);
        });
    }

    private function getPackageDimensions(Order $order): array
    {
        $itemCount = $order->items->sum('quantity');
        
        return [
            'length' => min(12, max(6, $itemCount * 2)),
            'width' => min(12, max(6, $itemCount * 1.5)),
            'height' => min(12, max(3, $itemCount * 0.5))
        ];
    }
}