<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\AuditLog;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Request;

class AuditLoggingService
{
    private const SENSITIVE_FIELDS = [
        'password',
        'password_confirmation',
        'secret',
        'token',
        'api_key',
        'credit_card',
        'cvv',
        'ssn',
    ];

    public function log(
        string $action,
        ?Model $entity = null,
        ?array $oldValues = null,
        ?array $newValues = null
    ): AuditLog {
        return AuditLog::create([
            'user_id' => Auth::id(),
            'action' => $action,
            'entity_type' => $entity ? get_class($entity) : null,
            'entity_id' => $entity?->getKey(),
            'old_values' => $oldValues ? $this->sanitize($oldValues) : null,
            'new_values' => $newValues ? $this->sanitize($newValues) : null,
            'ip_address' => Request::ip(),
            'user_agent' => Request::userAgent(),
        ]);
    }

    public function logModelChange(Model $model, string $action): AuditLog
    {
        $oldValues = null;
        $newValues = null;

        if ($action === 'updated') {
            $oldValues = $model->getOriginal();
            $newValues = $model->getAttributes();
        } elseif ($action === 'created') {
            $newValues = $model->getAttributes();
        } elseif ($action === 'deleted') {
            $oldValues = $model->getAttributes();
        }

        return $this->log($action, $model, $oldValues, $newValues);
    }

    public function logLogin(bool $success, ?string $email = null): AuditLog
    {
        $action = $success ? 'login_success' : 'login_failed';

        // Don't log email on failed attempts to prevent enumeration info in logs
        return AuditLog::create([
            'user_id' => Auth::id(),
            'action' => $action,
            'entity_type' => null,
            'entity_id' => null,
            'old_values' => null,
            'new_values' => $success ? null : ['attempt' => true],
            'ip_address' => Request::ip(),
            'user_agent' => Request::userAgent(),
        ]);
    }

    public function getLogsForEntity(string $entityType, int $entityId, int $limit = 50): array
    {
        return AuditLog::where('entity_type', $entityType)
            ->where('entity_id', $entityId)
            ->orderBy('created_at', 'desc')
            ->limit($limit)
            ->get()
            ->toArray();
    }

    public function getLogsForUser(int $userId, int $limit = 50): array
    {
        return AuditLog::where('user_id', $userId)
            ->orderBy('created_at', 'desc')
            ->limit($limit)
            ->get()
            ->toArray();
    }

    private function sanitize(array $values): array
    {
        return collect($values)->map(function ($value, $key) {
            if ($this->isSensitive($key)) {
                return '[REDACTED]';
            }

            return $value;
        })->toArray();
    }

    private function isSensitive(string $key): bool
    {
        $key = strtolower($key);

        foreach (self::SENSITIVE_FIELDS as $sensitive) {
            if (str_contains($key, $sensitive)) {
                return true;
            }
        }

        return false;
    }
}
