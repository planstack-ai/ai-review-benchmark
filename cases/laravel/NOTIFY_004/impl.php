<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Subscription;
use App\Notifications\SubscriptionExpiringNotification;
use App\Notifications\SubscriptionFinalReminderNotification;
use Illuminate\Support\Carbon;

class RenewalReminderService
{
    public function sendDueReminders(): array
    {
        $sent7d = $this->send7DayReminders();
        $sent1d = $this->send1DayReminders();

        return [
            '7_day_reminders' => $sent7d,
            '1_day_reminders' => $sent1d,
        ];
    }

    private function send7DayReminders(): int
    {
        $sevenDaysFromNow = now()->addDays(7);

        // BUG: Date comparison doesn't account for time portion
        // A subscription ending at 2024-01-15 23:59:59 might be caught
        // by this query multiple times over the 7-day window
        $subscriptions = Subscription::where('status', 'active')
            ->where('reminder_7d_sent', false)
            ->whereDate('current_period_end', '<=', $sevenDaysFromNow)
            ->whereDate('current_period_end', '>', now())
            ->with('user')
            ->get();

        $count = 0;
        foreach ($subscriptions as $subscription) {
            $this->sendReminder($subscription, '7d');
            $count++;
        }

        return $count;
    }

    private function send1DayReminders(): int
    {
        $oneDayFromNow = now()->addDay();

        $subscriptions = Subscription::where('status', 'active')
            ->where('reminder_1d_sent', false)
            ->whereDate('current_period_end', '<=', $oneDayFromNow)
            ->whereDate('current_period_end', '>', now())
            ->with('user')
            ->get();

        $count = 0;
        foreach ($subscriptions as $subscription) {
            $this->sendReminder($subscription, '1d');
            $count++;
        }

        return $count;
    }

    private function sendReminder(Subscription $subscription, string $type): void
    {
        $user = $subscription->user;

        // BUG: Checks if cancelled AFTER querying active subscriptions
        // But more importantly, doesn't check if subscription is still active
        // between query and send - could send to just-cancelled subscription
        if ($subscription->status === 'cancelled') {
            return;
        }

        $notification = $type === '7d'
            ? new SubscriptionExpiringNotification($subscription)
            : new SubscriptionFinalReminderNotification($subscription);

        // BUG: Sends immediately instead of scheduling for 9 AM user timezone
        $user->notify($notification);

        // BUG: Marks as sent even if notification might fail
        $subscription->update([
            "reminder_{$type}_sent" => true,
        ]);
    }

    public function resetReminders(int $subscriptionId): void
    {
        Subscription::where('id', $subscriptionId)->update([
            'reminder_7d_sent' => false,
            'reminder_1d_sent' => false,
        ]);
    }
}
