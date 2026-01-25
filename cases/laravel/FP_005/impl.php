<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Str;

class AuthenticationService
{
    public function login(string $email, string $password, bool $remember = false): array
    {
        $user = User::where('email', strtolower(trim($email)))->first();

        if (!$user || !Hash::check($password, $user->password)) {
            Log::warning("Failed login attempt for email: {$email}");

            return [
                'success' => false,
                'message' => 'Invalid credentials',
            ];
        }

        Auth::login($user, $remember);

        $user->update(['last_login_at' => now()]);

        Log::info("User {$user->id} logged in successfully");

        return [
            'success' => true,
            'user' => $user,
            'message' => 'Login successful',
        ];
    }

    public function logout(): bool
    {
        $userId = Auth::id();

        Auth::logout();

        if ($userId) {
            Log::info("User {$userId} logged out");
        }

        return true;
    }

    public function sendPasswordResetLink(string $email): array
    {
        $user = User::where('email', strtolower(trim($email)))->first();

        if (!$user) {
            // Don't reveal if user exists
            return [
                'success' => true,
                'message' => 'If your email exists, you will receive a reset link',
            ];
        }

        $status = Password::sendResetLink(['email' => $user->email]);

        Log::info("Password reset requested for user {$user->id}");

        return [
            'success' => $status === Password::RESET_LINK_SENT,
            'message' => 'If your email exists, you will receive a reset link',
        ];
    }

    public function resetPassword(string $email, string $password, string $token): array
    {
        $status = Password::reset(
            [
                'email' => $email,
                'password' => $password,
                'password_confirmation' => $password,
                'token' => $token,
            ],
            function ($user, $password) {
                $user->forceFill([
                    'password' => Hash::make($password),
                    'remember_token' => Str::random(60),
                ])->save();

                Log::info("Password reset completed for user {$user->id}");
            }
        );

        return [
            'success' => $status === Password::PASSWORD_RESET,
            'message' => $status === Password::PASSWORD_RESET
                ? 'Password reset successfully'
                : 'Unable to reset password',
        ];
    }
}
