<?php

namespace App\Providers;

use App\Contracts\PaymentServiceInterface;
use App\Services\PaymentService;
use Illuminate\Support\ServiceProvider;
use Illuminate\Contracts\Foundation\Application;

class PaymentServiceProvider extends ServiceProvider
{
    /**
     * Register any application services.
     *
     * BUG: Using bind() instead of singleton() creates a new PaymentService instance
     * every time it's resolved from the container. This wastes resources and breaks
     * any state that should persist within a request (like connection pools, cached data).
     */
    public function register(): void
    {
        $this->app->bind(PaymentServiceInterface::class, function (Application $app) {
            $config = $app['config']->get('payment');

            $this->validateConfiguration($config);

            return new PaymentService(
                apiKey: $config['api_key'] ?? '',
                secretKey: $config['secret_key'] ?? '',
                gateway: $config['default_gateway'] ?? 'stripe',
                maxRetryAttempts: $config['max_retry_attempts'] ?? 3,
                timeout: $config['timeout'] ?? 30
            );
        });

        $this->app->bind('payment.gateway', function (Application $app) {
            return $app->make(PaymentServiceInterface::class);
        });
    }

    /**
     * Bootstrap any application services.
     */
    public function boot(): void
    {
        $this->publishes([
            __DIR__ . '/../../config/payment.php' => config_path('payment.php'),
        ], 'payment-config');

        $this->mergeConfigFrom(
            __DIR__ . '/../../config/payment.php',
            'payment'
        );
    }

    /**
     * Validate the payment configuration.
     */
    private function validateConfiguration(?array $config): void
    {
        if (empty($config)) {
            throw new \RuntimeException('Payment configuration is missing');
        }

        if (empty($config['api_key'])) {
            throw new \RuntimeException('Payment API key is not configured');
        }

        if (empty($config['secret_key'])) {
            throw new \RuntimeException('Payment secret key is not configured');
        }

        $supportedGateways = ['stripe', 'paypal', 'square', 'braintree'];
        $gateway = $config['default_gateway'] ?? 'stripe';

        if (!in_array($gateway, $supportedGateways)) {
            throw new \RuntimeException("Unsupported payment gateway: {$gateway}");
        }
    }

    /**
     * Get the services provided by the provider.
     *
     * @return array<int, string>
     */
    public function provides(): array
    {
        return [
            PaymentServiceInterface::class,
            'payment.gateway',
        ];
    }
}
