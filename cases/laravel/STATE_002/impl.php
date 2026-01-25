<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Subscription;
use Illuminate\Support\Carbon;

class SubscriptionService
{
    public function activate(int $subscriptionId): array
    {
        $subscription = Subscription::findOrFail($subscriptionId);

        // BUG: Allows activation from any state, not just trial
        // Should only allow: trial → active, paused → active
        $subscription->update([
            'status' => 'active',
            'current_period_ends_at' => now()->addMonth(),
        ]);

        return [
            'success' => true,
            'subscription' => $subscription,
        ];
    }

    public function pause(int $subscriptionId): array
    {
        $subscription = Subscription::findOrFail($subscriptionId);

        if ($subscription->status !== 'active') {
            return [
                'success' => false,
                'message' => 'Only active subscriptions can be paused',
            ];
        }

        $subscription->update([
            'status' => 'paused',
            'paused_at' => now(),
        ]);

        return [
            'success' => true,
            'subscription' => $subscription,
        ];
    }

    public function resume(int $subscriptionId): array
    {
        $subscription = Subscription::findOrFail($subscriptionId);

        if ($subscription->status !== 'paused') {
            return [
                'success' => false,
                'message' => 'Only paused subscriptions can be resumed',
            ];
        }

        $pausedDays = $subscription->paused_at->diffInDays(now());

        $subscription->update([
            'status' => 'active',
            'paused_at' => null,
            'current_period_ends_at' => $subscription->current_period_ends_at->addDays($pausedDays),
        ]);

        return [
            'success' => true,
            'subscription' => $subscription,
        ];
    }

    public function cancel(int $subscriptionId): array
    {
        $subscription = Subscription::findOrFail($subscriptionId);

        // BUG: Allows cancelling already cancelled or expired subscriptions
        // Should check current state first
        $subscription->update([
            'status' => 'cancelled',
            'cancelled_at' => now(),
        ]);

        return [
            'success' => true,
            'subscription' => $subscription,
        ];
    }

    public function checkExpiration(int $subscriptionId): array
    {
        $subscription = Subscription::findOrFail($subscriptionId);

        if ($subscription->status === 'trial' && $subscription->trial_ends_at->isPast()) {
            $subscription->update(['status' => 'expired']);

            return ['expired' => true, 'reason' => 'Trial ended'];
        }

        if ($subscription->status === 'active' && $subscription->current_period_ends_at->isPast()) {
            $subscription->update(['status' => 'expired']);

            return ['expired' => true, 'reason' => 'Payment not renewed'];
        }

        return ['expired' => false];
    }
}
