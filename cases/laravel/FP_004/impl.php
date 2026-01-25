<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Models\Notification;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;

class NotificationService
{
    private User $user;
    private string $type;
    private array $data;

    public function __construct(User $user, string $type, array $data = [])
    {
        $this->user = $user;
        $this->type = $type;
        $this->data = $data;
    }

    public function sendEmail(): bool
    {
        try {
            $notification = $this->createNotificationRecord('email');

            Mail::to($this->user->email)->queue(
                $this->buildEmailNotification()
            );

            $notification->update(['sent_at' => now()]);

            Log::info("Email notification sent to user {$this->user->id}", [
                'type' => $this->type,
                'notification_id' => $notification->id,
            ]);

            return true;
        } catch (\Exception $e) {
            Log::error("Failed to send email notification: {$e->getMessage()}", [
                'user_id' => $this->user->id,
                'type' => $this->type,
            ]);

            return false;
        }
    }

    public function sendPush(): bool
    {
        try {
            if (!$this->user->push_token) {
                Log::warning("User {$this->user->id} has no push token");
                return false;
            }

            $notification = $this->createNotificationRecord('push');

            // Push notification logic would go here
            // Using a push service like Firebase, OneSignal, etc.

            $notification->update(['sent_at' => now()]);

            Log::info("Push notification sent to user {$this->user->id}", [
                'type' => $this->type,
            ]);

            return true;
        } catch (\Exception $e) {
            Log::error("Failed to send push notification: {$e->getMessage()}");
            return false;
        }
    }

    private function createNotificationRecord(string $channel): Notification
    {
        return Notification::create([
            'user_id' => $this->user->id,
            'type' => $this->type,
            'channel' => $channel,
            'data' => $this->data,
        ]);
    }

    private function buildEmailNotification()
    {
        // Return appropriate Mailable based on type
        return new \App\Mail\GenericNotification($this->type, $this->data);
    }
}
