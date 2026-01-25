<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Upload;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Str;

class FileUploadService
{
    private const MAX_SIZE = 10 * 1024 * 1024; // 10MB
    private const ALLOWED_MIMES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'application/pdf',
    ];

    public function upload(UploadedFile $file, int $userId, string $disk = 'local'): array
    {
        // Validate mime type using the actual file content, not just extension
        $mimeType = $file->getMimeType();

        if (!in_array($mimeType, self::ALLOWED_MIMES, true)) {
            return [
                'success' => false,
                'message' => 'File type not allowed',
            ];
        }

        // Validate file size
        if ($file->getSize() > self::MAX_SIZE) {
            return [
                'success' => false,
                'message' => 'File size exceeds maximum allowed',
            ];
        }

        // Generate unique filename to prevent overwriting and path traversal
        $extension = $file->getClientOriginalExtension();
        $safeExtension = preg_replace('/[^a-zA-Z0-9]/', '', $extension);
        $storedName = Str::uuid() . '.' . $safeExtension;

        // Store file
        $path = $file->storeAs('uploads', $storedName, $disk);

        if (!$path) {
            return [
                'success' => false,
                'message' => 'Failed to store file',
            ];
        }

        // Create database record
        $upload = Upload::create([
            'user_id' => $userId,
            'original_name' => $this->sanitizeFilename($file->getClientOriginalName()),
            'stored_name' => $storedName,
            'mime_type' => $mimeType,
            'size' => $file->getSize(),
            'disk' => $disk,
        ]);

        return [
            'success' => true,
            'upload' => $upload,
        ];
    }

    public function delete(int $uploadId, int $userId): array
    {
        $upload = Upload::where('id', $uploadId)
            ->where('user_id', $userId)
            ->first();

        if (!$upload) {
            return [
                'success' => false,
                'message' => 'Upload not found or access denied',
            ];
        }

        // Delete file from storage
        Storage::disk($upload->disk)->delete('uploads/' . $upload->stored_name);

        // Delete database record
        $upload->delete();

        return ['success' => true];
    }

    public function getUrl(int $uploadId, int $userId): ?string
    {
        $upload = Upload::where('id', $uploadId)
            ->where('user_id', $userId)
            ->first();

        if (!$upload) {
            return null;
        }

        return Storage::disk($upload->disk)->url('uploads/' . $upload->stored_name);
    }

    private function sanitizeFilename(string $filename): string
    {
        // Remove any path traversal attempts and non-printable characters
        $filename = basename($filename);
        $filename = preg_replace('/[^\x20-\x7E]/', '', $filename);

        return mb_substr($filename, 0, 255);
    }
}
