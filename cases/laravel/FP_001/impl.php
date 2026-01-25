<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;
use App\Mail\WelcomeEmail;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Log;

class UserManagementService
{
    private ?User $user;
    private array $errors = [];

    public function __construct(?User $user = null)
    {
        $this->user = $user;
    }

    public function create(array $userParams): User|false
    {
        $this->user = new User($this->sanitizedParams($userParams));

        if ($this->validateUserData() && $this->user->save()) {
            $this->sendWelcomeEmail();
            $this->logUserCreation();

            return $this->user;
        }

        $this->collectErrors();
        return false;
    }

    public function update(array $userParams): User|false
    {
        if (!$this->user) {
            return false;
        }

        $this->user->fill($this->sanitizedParams($userParams));

        if ($this->validateUserData() && $this->user->save()) {
            $this->logUserUpdate();

            return $this->user;
        }

        $this->collectErrors();
        return false;
    }

    public function destroy(): bool
    {
        if (!$this->user) {
            return false;
        }

        if ($this->user->delete()) {
            $this->cleanupUserData();
            $this->logUserDeletion();

            return true;
        }

        $this->collectErrors();
        return false;
    }

    public function findByEmail(string $email): ?User
    {
        $this->user = User::where('email', $this->normalizeEmail($email))->first();

        return $this->user;
    }

    public function activate(): bool
    {
        if (!$this->user) {
            return false;
        }

        return $this->user->update([
            'active' => true,
            'activated_at' => now(),
        ]);
    }

    public function deactivate(): bool
    {
        if (!$this->user) {
            return false;
        }

        return $this->user->update([
            'active' => false,
            'deactivated_at' => now(),
        ]);
    }

    public function getErrors(): array
    {
        return $this->errors;
    }

    private function sanitizedParams(array $params): array
    {
        return collect($params)->only([
            'first_name', 'last_name', 'email', 'phone', 'role'
        ])->toArray();
    }

    private function validateUserData(): bool
    {
        if (empty($this->user->email)) {
            return false;
        }

        if (!$this->validEmailFormat()) {
            return false;
        }

        if ($this->duplicateEmailExists()) {
            return false;
        }

        return true;
    }

    private function validEmailFormat(): bool
    {
        return filter_var($this->user->email, FILTER_VALIDATE_EMAIL) !== false;
    }

    private function duplicateEmailExists(): bool
    {
        $existingUser = User::where('email', $this->user->email)->first();

        return $existingUser && $existingUser->id !== $this->user->id;
    }

    private function normalizeEmail(string $email): string
    {
        return strtolower(trim($email));
    }

    private function collectErrors(): void
    {
        $this->errors = $this->user->errors?->all() ?? [];
    }

    private function sendWelcomeEmail(): void
    {
        Mail::to($this->user)->queue(new WelcomeEmail($this->user));
    }

    private function cleanupUserData(): void
    {
        // Posts and comments are cascade deleted via foreign keys
        // This method is for any additional cleanup needed
    }

    private function logUserCreation(): void
    {
        Log::info("User created: {$this->user->email} (ID: {$this->user->id})");
    }

    private function logUserUpdate(): void
    {
        Log::info("User updated: {$this->user->email} (ID: {$this->user->id})");
    }

    private function logUserDeletion(): void
    {
        Log::info("User deleted: {$this->user->email}");
    }
}
