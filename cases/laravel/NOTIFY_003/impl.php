<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Notifications\PasswordResetNotification;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class PasswordResetService
{
    private const TOKEN_EXPIRY_MINUTES = 60;

    public function sendResetLink(string $email): array
    {
        $user = User::where('email', strtolower($email))->first();

        // Security: Same response whether user exists or not
        $response = [
            'success' => true,
            'message' => 'If your email exists, you will receive a reset link',
        ];

        if (!$user) {
            \Log::info("Password reset requested for non-existent email: {$email}");

            return $response;
        }

        // Delete existing tokens
        DB::table('password_resets')->where('email', $user->email)->delete();

        $token = Str::random(64);

        DB::table('password_resets')->insert([
            'email' => $user->email,
            'token' => $token, // BUG: Storing plain token instead of hashed
            'created_at' => now(),
        ]);

        // BUG: Sending plain token in email, storing plain token in DB
        // If DB is compromised, attacker has valid reset tokens
        $user->notify(new PasswordResetNotification($token));

        \Log::info("Password reset link sent to user {$user->id}");

        return $response;
    }

    public function validateToken(string $email, string $token): bool
    {
        $reset = DB::table('password_resets')
            ->where('email', $email)
            ->where('token', $token) // BUG: Comparing plain tokens
            ->first();

        if (!$reset) {
            return false;
        }

        // Check expiry
        $createdAt = \Carbon\Carbon::parse($reset->created_at);
        if ($createdAt->addMinutes(self::TOKEN_EXPIRY_MINUTES)->isPast()) {
            return false;
        }

        return true;
    }

    public function resetPassword(string $email, string $token, string $newPassword): array
    {
        if (!$this->validateToken($email, $token)) {
            return [
                'success' => false,
                'message' => 'Invalid or expired token',
            ];
        }

        $user = User::where('email', $email)->first();

        if (!$user) {
            return [
                'success' => false,
                'message' => 'User not found',
            ];
        }

        $user->update([
            'password' => Hash::make($newPassword),
        ]);

        // Delete used token
        DB::table('password_resets')->where('email', $email)->delete();

        \Log::info("Password reset completed for user {$user->id}");

        return [
            'success' => true,
            'message' => 'Password reset successfully',
        ];
    }
}
