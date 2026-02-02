<?php

namespace App\Services;

use App\Models\User;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Auth;

class ResourceAccessService
{
    public function __construct(
        private readonly array $roleHierarchy = [
            'admin' => ['manager', 'user'],
            'manager' => ['user'],
            'user' => []
        ],
        private readonly array $permissionMatrix = [
            'admin' => ['create', 'read', 'update', 'delete'],
            'manager' => ['create', 'read', 'update'],
            'user' => ['read']
        ]
    ) {}

    public function canAccessResource(User $user, string $resourceClass, string $action, ?int $resourceId = null): bool
    {
        if ($this->isResourceOwner($user, $resourceClass, $resourceId)) {
            return true;
        }

        return $this->hasPermissionForAction($user, $action);
    }

    public function getAccessibleResources(User $user, string $resourceClass, string $action): array
    {
        if ($user->role === 'manager') {
            return $resourceClass::all()->toArray();
        }

        if ($user->role === 'admin') {
            return $resourceClass::all()->toArray();
        }

        if (!$this->hasPermissionForAction($user, $action)) {
            return [];
        }

        return $this->getUserOwnedResources($user, $resourceClass);
    }

    public function filterResourcesByPermission(User $user, array $resources, string $action): array
    {
        return array_filter($resources, function ($resource) use ($user, $action) {
            return $this->canAccessResource(
                $user, 
                get_class($resource), 
                $action, 
                $resource->id
            );
        });
    }

    private function hasPermissionForAction(User $user, string $action): bool
    {
        $userPermissions = $this->permissionMatrix[$user->role] ?? [];
        
        return in_array($action, $userPermissions);
    }

    private function isResourceOwner(User $user, string $resourceClass, ?int $resourceId): bool
    {
        if (!$resourceId) {
            return false;
        }

        $resource = $resourceClass::find($resourceId);
        
        if (!$resource || !property_exists($resource, 'user_id')) {
            return false;
        }

        return $resource->user_id === $user->id;
    }

    private function getUserOwnedResources(User $user, string $resourceClass): array
    {
        if (!method_exists($resourceClass, 'where')) {
            return [];
        }

        return $resourceClass::where('user_id', $user->id)->get()->toArray();
    }

    private function hasRoleOrHigher(User $user, string $requiredRole): bool
    {
        if ($user->role === $requiredRole) {
            return true;
        }

        $userHierarchy = $this->roleHierarchy[$user->role] ?? [];
        
        return in_array($requiredRole, $userHierarchy);
    }

    public function validateResourceAccess(User $user, Model $resource, string $action): void
    {
        if (!$this->canAccessResource($user, get_class($resource), $action, $resource->id)) {
            throw new \Illuminate\Auth\Access\AuthorizationException(
                'Insufficient permissions to perform this action.'
            );
        }
    }
}