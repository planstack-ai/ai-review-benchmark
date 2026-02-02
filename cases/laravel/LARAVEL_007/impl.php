<?php

namespace Tests\Feature;

use Tests\TestCase;
use App\Models\User;
use App\Services\EmailService;
use Illuminate\Support\Facades\Mail;
use Illuminate\Foundation\Testing\RefreshDatabase;
use App\Mail\WelcomeEmail;
use App\Mail\NotificationEmail;

class EmailServiceTest extends TestCase
{
    use RefreshDatabase;

    private EmailService $emailService;
    private User $user;

    protected function setUp(): void
    {
        parent::setUp();

        Mail::fake();

        $this->user = User::factory()->create([
            'email' => 'test@example.com',
            'name' => 'Test User',
        ]);

        $this->emailService = app(EmailService::class);
    }

    /**
     * BUG: Missing parent::tearDown() call causes Mail::fake() to leak to subsequent tests.
     * This can cause false positives or false negatives in other test files.
     */
    protected function tearDown(): void
    {
        $this->user = null;
        $this->emailService = null;
        // BUG: Not calling parent::tearDown() - mock leaks to next test
    }

    public function test_welcome_email_is_sent_to_new_user(): void
    {
        $result = $this->emailService->sendWelcomeEmail($this->user);

        $this->assertTrue($result);
        Mail::assertSent(WelcomeEmail::class, function ($mail) {
            return $mail->hasTo($this->user->email);
        });
    }

    public function test_welcome_email_fails_for_user_without_email(): void
    {
        $userWithoutEmail = User::factory()->create(['email' => '']);

        $result = $this->emailService->sendWelcomeEmail($userWithoutEmail);

        $this->assertFalse($result);
        Mail::assertNotSent(WelcomeEmail::class);
    }

    public function test_notification_email_is_sent_with_correct_content(): void
    {
        $subject = 'Test Subject';
        $message = 'Test Message';

        $result = $this->emailService->sendNotificationEmail(
            $this->user,
            $subject,
            $message
        );

        $this->assertTrue($result);
        Mail::assertSent(NotificationEmail::class, function ($mail) use ($subject) {
            return $mail->hasTo($this->user->email) && $mail->subject === $subject;
        });
    }

    public function test_bulk_notifications_sends_to_all_users(): void
    {
        $users = User::factory()->count(3)->create();
        $userIds = $users->pluck('id')->toArray();

        $results = $this->emailService->sendBulkNotifications(
            $userIds,
            'Bulk Subject',
            'Bulk Message'
        );

        $this->assertCount(3, $results);
        foreach ($results as $userId => $sent) {
            $this->assertTrue($sent);
        }
        Mail::assertSentCount(3);
    }

    public function test_email_is_not_sent_to_invalid_email_address(): void
    {
        $userWithInvalidEmail = User::factory()->create([
            'email' => 'not-an-email',
        ]);

        $result = $this->emailService->sendWelcomeEmail($userWithInvalidEmail);

        $this->assertFalse($result);
        Mail::assertNothingSent();
    }

    public function test_email_stats_are_tracked_correctly(): void
    {
        $this->emailService->sendWelcomeEmail($this->user);
        $this->emailService->sendNotificationEmail($this->user, 'Test', 'Message');

        $stats = $this->emailService->getEmailStats($this->user);

        $this->assertEquals(2, $stats['total_sent']);
        $this->assertEquals(1, $stats['welcome_emails']);
        $this->assertEquals(1, $stats['notification_emails']);
    }

    public function test_password_reset_email_contains_token(): void
    {
        $token = 'reset-token-123';

        $result = $this->emailService->sendPasswordResetEmail($this->user, $token);

        $this->assertTrue($result);
        Mail::assertSent(\App\Mail\PasswordResetEmail::class, function ($mail) use ($token) {
            return $mail->hasTo($this->user->email) && $mail->token === $token;
        });
    }
}
