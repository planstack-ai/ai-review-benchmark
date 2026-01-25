<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\NotificationLog;
use App\Models\User;
use App\Notifications\BulkNotification;

class NotificationDispatchService
{
    public function sendToAllUsers(string $type, array $data): array
    {
        // BUG: Loads all users into memory
        $users = User::where('email_notifications', true)->get();

        $sent = 0;
        $failed = 0;

        foreach ($users as $user) {
            try {
                // BUG: Sends synchronously in loop - very slow for many users
                // Each notification blocks until sent
                $user->notify(new BulkNotification($type, $data));

                // BUG: Individual INSERT for each log entry
                NotificationLog::create([
                    'user_id' => $user->id,
                    'type' => $type,
                    'status' => 'sent',
                ]);

                $sent++;
            } catch (\Exception $e) {
                NotificationLog::create([
                    'user_id' => $user->id,
                    'type' => $type,
                    'status' => 'failed',
                ]);

                $failed++;
            }
        }

        return [
            'sent' => $sent,
            'failed' => $failed,
        ];
    }

    public function sendToSegment(array $userIds, string $type, array $data): array
    {
        $sent = 0;

        foreach ($userIds as $userId) {
            // BUG: Query inside loop - N queries for N users
            $user = User::find($userId);

            if ($user && $user->email_notifications) {
                $user->notify(new BulkNotification($type, $data));
                $sent++;
            }
        }

        return ['sent' => $sent];
    }
}
