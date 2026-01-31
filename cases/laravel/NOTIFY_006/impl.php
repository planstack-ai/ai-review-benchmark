<?php

namespace App\Services;

use App\Models\User;
use App\Mail\NewsletterMail;
use App\Mail\WelcomeMail;
use App\Mail\PromotionalMail;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Log;
use Illuminate\Database\Eloquent\Collection;

class EmailCampaignService
{
    public function __construct(
        private readonly int $batchSize = 50,
        private readonly int $delayBetweenBatches = 30
    ) {}

    public function sendNewsletterToAllUsers(string $subject, string $content): array
    {
        $users = $this->getActiveUsers();
        $results = $this->processEmailCampaign($users, 'newsletter', [
            'subject' => $subject,
            'content' => $content
        ]);

        Log::info('Newsletter campaign completed', [
            'total_users' => $users->count(),
            'successful_sends' => $results['success'],
            'failed_sends' => $results['failed']
        ]);

        return $results;
    }

    public function sendWelcomeEmailsToNewUsers(): array
    {
        $newUsers = $this->getNewUsers();
        
        if ($newUsers->isEmpty()) {
            return ['success' => 0, 'failed' => 0, 'message' => 'No new users found'];
        }

        return $this->processEmailCampaign($newUsers, 'welcome');
    }

    public function sendPromotionalEmail(array $userIds, string $promoCode, float $discountPercent): array
    {
        $users = User::whereIn('id', $userIds)
            ->where('marketing_emails_enabled', true)
            ->get();

        return $this->processEmailCampaign($users, 'promotional', [
            'promo_code' => $promoCode,
            'discount_percent' => $discountPercent
        ]);
    }

    private function processEmailCampaign(Collection $users, string $emailType, array $data = []): array
    {
        $successCount = 0;
        $failedCount = 0;

        $users->each(function (User $user) use ($emailType, $data, &$successCount, &$failedCount) {
            try {
                $this->sendEmailByType($user, $emailType, $data);
                $successCount++;
            } catch (\Exception $e) {
                $failedCount++;
                Log::error('Failed to send email', [
                    'user_id' => $user->id,
                    'email_type' => $emailType,
                    'error' => $e->getMessage()
                ]);
            }
        });

        return [
            'success' => $successCount,
            'failed' => $failedCount,
            'total' => $users->count()
        ];
    }

    private function sendEmailByType(User $user, string $emailType, array $data): void
    {
        $mailable = match ($emailType) {
            'newsletter' => new NewsletterMail($data['subject'], $data['content']),
            'welcome' => new WelcomeMail($user),
            'promotional' => new PromotionalMail($data['promo_code'], $data['discount_percent']),
            default => throw new \InvalidArgumentException("Unknown email type: {$emailType}")
        };

        Mail::to($user->email)->send($mailable);
    }

    private function getActiveUsers(): Collection
    {
        return User::where('email_verified_at', '!=', null)
            ->where('is_active', true)
            ->where('marketing_emails_enabled', true)
            ->get();
    }

    private function getNewUsers(): Collection
    {
        return User::where('created_at', '>=', now()->subDays(7))
            ->whereNull('welcome_email_sent_at')
            ->get();
    }

    private function validateEmailData(array $data, string $emailType): void
    {
        $requiredFields = match ($emailType) {
            'newsletter' => ['subject', 'content'],
            'promotional' => ['promo_code', 'discount_percent'],
            'welcome' => [],
            default => []
        };

        foreach ($requiredFields as $field) {
            if (!isset($data[$field])) {
                throw new \InvalidArgumentException("Missing required field: {$field}");
            }
        }
    }
}