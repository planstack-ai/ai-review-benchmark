# Existing Codebase

## Schema

```php
Schema::create('payments', function (Blueprint $table) {
    $table->id();
    $table->foreignId('order_id')->constrained();
    $table->decimal('amount', 10, 2);
    $table->string('status'); // pending, processing, completed, failed, refunding, refunded
    $table->string('gateway_reference')->nullable();
    $table->text('failure_reason')->nullable();
    $table->timestamps();
});
```

## Gateway Interface

```php
interface PaymentGateway
{
    public function charge(float $amount, array $paymentDetails): GatewayResult;
    public function refund(string $reference, float $amount): GatewayResult;
}

class GatewayResult
{
    public bool $success;
    public ?string $reference;
    public ?string $error;
}
```
