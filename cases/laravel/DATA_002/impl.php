<?php

namespace App\Services;

use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Validator;
use Illuminate\Validation\ValidationException;
use Illuminate\Database\Eloquent\ModelNotFoundException;

class UserRegistrationService
{
    public function __construct(
        private User $userModel
    ) {}

    public function registerUser(array $userData): User
    {
        $this->validateUserData($userData);
        
        $processedData = $this->prepareUserData($userData);
        
        return $this->createUser($processedData);
    }

    public function updateUserEmail(int $userId, string $newEmail): User
    {
        $user = $this->findUserById($userId);
        
        $this->validateEmailUpdate($newEmail, $userId);
        
        $user->email = $this->normalizeEmail($newEmail);
        $user->email_verified_at = null;
        $user->save();
        
        return $user->fresh();
    }

    public function bulkRegisterUsers(array $usersData): array
    {
        $registeredUsers = [];
        
        foreach ($usersData as $userData) {
            try {
                $registeredUsers[] = $this->registerUser($userData);
            } catch (ValidationException $e) {
                continue;
            }
        }
        
        return $registeredUsers;
    }

    private function validateUserData(array $userData): void
    {
        $validator = Validator::make($userData, [
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:users',
            'password' => 'required|string|min:8|confirmed',
        ]);

        if ($validator->fails()) {
            throw new ValidationException($validator);
        }
    }

    private function validateEmailUpdate(string $email, int $userId): void
    {
        $validator = Validator::make(['email' => $email], [
            'email' => 'required|email|unique:users,email,' . $userId,
        ]);

        if ($validator->fails()) {
            throw new ValidationException($validator);
        }
    }

    private function prepareUserData(array $userData): array
    {
        return [
            'name' => trim($userData['name']),
            'email' => $this->normalizeEmail($userData['email']),
            'password' => Hash::make($userData['password']),
            'email_verified_at' => null,
        ];
    }

    private function normalizeEmail(string $email): string
    {
        return strtolower(trim($email));
    }

    private function createUser(array $userData): User
    {
        return $this->userModel->create($userData);
    }

    private function findUserById(int $userId): User
    {
        $user = $this->userModel->find($userId);
        
        if (!$user) {
            throw new ModelNotFoundException('User not found');
        }
        
        return $user;
    }

    public function checkEmailAvailability(string $email): bool
    {
        $normalizedEmail = $this->normalizeEmail($email);
        
        return !$this->userModel->where('email', $normalizedEmail)->exists();
    }
}