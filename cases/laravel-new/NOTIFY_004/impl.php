<?php

namespace App\Services;

use App\Models\User;
use App\Models\EmailTemplate;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Log;
use Illuminate\Mail\Mailable;

class EmailNotificationService
{
    public function __construct(
        private readonly EmailTemplate $emailTemplate
    ) {}

    public function sendWelcomeEmail(User $user): bool
    {
        try {
            $template = $this->getWelcomeTemplate();
            $compiledContent = $this->compileTemplate($template, $user);
            
            return $this->dispatchEmail($user->email, $compiledContent);
        } catch (\Exception $e) {
            Log::error('Failed to send welcome email', [
                'user_id' => $user->id,
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }

    public function sendPasswordResetEmail(User $user, string $resetToken): bool
    {
        try {
            $template = $this->getPasswordResetTemplate();
            $compiledContent = $this->compileTemplateWithToken($template, $user, $resetToken);
            
            return $this->dispatchEmail($user->email, $compiledContent);
        } catch (\Exception $e) {
            Log::error('Failed to send password reset email', [
                'user_id' => $user->id,
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }

    public function sendAccountVerificationEmail(User $user): bool
    {
        if ($user->hasVerifiedEmail()) {
            return true;
        }

        try {
            $template = $this->getVerificationTemplate();
            $compiledContent = $this->compileTemplate($template, $user);
            
            return $this->dispatchEmail($user->email, $compiledContent);
        } catch (\Exception $e) {
            Log::error('Failed to send verification email', [
                'user_id' => $user->id,
                'error' => $e->getMessage()
            ]);
            return false;
        }
    }

    private function getWelcomeTemplate(): EmailTemplate
    {
        return $this->emailTemplate->where('type', 'welcome')->firstOrFail();
    }

    private function getPasswordResetTemplate(): EmailTemplate
    {
        return $this->emailTemplate->where('type', 'password_reset')->firstOrFail();
    }

    private function getVerificationTemplate(): EmailTemplate
    {
        return $this->emailTemplate->where('type', 'verification')->firstOrFail();
    }

    private function compileTemplate(EmailTemplate $template, User $user): string
    {
        $content = $template->content;
        
        $content = str_replace('{{ $user->email }}', $user->email, $content);
        $content = str_replace('{{ $user->name }}', $user->name, $content);
        $content = str_replace('{{ $app_name }}', config('app.name'), $content);
        $content = str_replace('{{ $app_url }}', config('app.url'), $content);
        
        return $content;
    }

    private function compileTemplateWithToken(EmailTemplate $template, User $user, string $token): string
    {
        $content = $this->compileTemplate($template, $user);
        $resetUrl = config('app.url') . '/password/reset/' . $token;
        
        $content = str_replace('{{ $reset_url }}', $resetUrl, $content);
        $content = str_replace('{{ $token }}', $token, $content);
        
        return $content;
    }

    private function dispatchEmail(string $email, string $content): bool
    {
        Mail::html($content, function ($message) use ($email) {
            $message->to($email)
                   ->subject('Notification from ' . config('app.name'));
        });

        return true;
    }

    public function validateTemplateVariables(EmailTemplate $template): array
    {
        $requiredVariables = ['{{ $user->email }}', '{{ $user->name }}', '{{ $app_name }}'];
        $missingVariables = [];

        foreach ($requiredVariables as $variable) {
            if (!str_contains($template->content, $variable)) {
                $missingVariables[] = $variable;
            }
        }

        return $missingVariables;
    }
}