<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\User;

class UserSearchService
{
    public function search(string $query, int $perPage = 20): array
    {
        // BUG: Using LIKE with leading wildcard prevents index usage
        // Full table scan on large user tables
        $users = User::where('name', 'LIKE', "%{$query}%")
            ->orWhere('email', 'LIKE', "%{$query}%")
            ->paginate($perPage);

        return [
            'users' => $users->items(),
            'total' => $users->total(),
        ];
    }

    public function findByEmail(string $email): ?User
    {
        // BUG: LOWER() function prevents index usage on email column
        // Even though email has unique index, this causes full scan
        return User::whereRaw('LOWER(email) = ?', [strtolower($email)])->first();
    }

    public function getRecentUsers(int $limit = 100): array
    {
        // BUG: Ordering by non-indexed column causes filesort
        // name column is not indexed
        return User::orderBy('name')
            ->limit($limit)
            ->get()
            ->toArray();
    }

    public function getUsersWithStatus(string $status): array
    {
        // BUG: No index on status column, full table scan
        // Also selects all columns when only some needed
        return User::where('status', $status)
            ->get()
            ->toArray();
    }
}
