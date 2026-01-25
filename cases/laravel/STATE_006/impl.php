<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Candidate;
use App\Models\Interview;
use App\Models\User;

class InterviewService
{
    private const STAGE_ORDER = [
        'applied' => 0,
        'phone_screen' => 1,
        'technical' => 2,
        'onsite' => 3,
        'offer' => 4,
    ];

    public function scheduleInterview(int $candidateId, string $type, User $interviewer, string $scheduledAt): array
    {
        $candidate = Candidate::findOrFail($candidateId);

        if (in_array($candidate->status, ['rejected', 'accepted', 'declined'])) {
            return [
                'success' => false,
                'message' => 'Cannot schedule interview for candidate in terminal state',
            ];
        }

        $interview = Interview::create([
            'candidate_id' => $candidateId,
            'type' => $type,
            'interviewer_id' => $interviewer->id,
            'scheduled_at' => $scheduledAt,
        ]);

        return ['success' => true, 'interview' => $interview];
    }

    public function recordResult(int $interviewId, string $result, string $feedback): array
    {
        $interview = Interview::findOrFail($interviewId);
        $candidate = $interview->candidate;

        $interview->update([
            'result' => $result,
            'feedback' => $feedback,
        ]);

        if ($result === 'failed') {
            $candidate->update(['status' => 'rejected']);

            return ['success' => true, 'candidate_status' => 'rejected'];
        }

        // BUG: Advances to next stage without checking if current stage matches interview type
        // Could skip stages if interviews are recorded out of order
        $nextStage = $this->getNextStage($interview->type);

        if ($nextStage) {
            $candidate->update(['status' => $nextStage]);
        }

        return ['success' => true, 'candidate_status' => $candidate->status];
    }

    public function makeOffer(int $candidateId): array
    {
        $candidate = Candidate::findOrFail($candidateId);

        // BUG: Only checks if status is 'onsite', not if onsite interview passed
        // Should verify the onsite interview has result='passed'
        if ($candidate->status !== 'onsite') {
            return [
                'success' => false,
                'message' => 'Candidate must complete onsite interview',
            ];
        }

        $candidate->update(['status' => 'offer']);

        return ['success' => true, 'candidate' => $candidate];
    }

    public function respondToOffer(int $candidateId, bool $accepted): array
    {
        $candidate = Candidate::findOrFail($candidateId);

        if ($candidate->status !== 'offer') {
            return [
                'success' => false,
                'message' => 'Candidate does not have a pending offer',
            ];
        }

        $candidate->update([
            'status' => $accepted ? 'accepted' : 'declined',
        ]);

        return ['success' => true, 'candidate' => $candidate];
    }

    private function getNextStage(string $currentType): ?string
    {
        return match ($currentType) {
            'phone_screen' => 'technical',
            'technical' => 'onsite',
            'onsite' => null, // Offer made separately
            default => null,
        };
    }
}
