# Expected Critique

## Critical Bug: Interview Stage Can Be Skipped

### Location
`recordResult()` method:
```php
$nextStage = $this->getNextStage($interview->type);

if ($nextStage) {
    $candidate->update(['status' => $nextStage]);
}
```

### Problem
The code advances the candidate to the next stage based on the **interview type** rather than verifying the candidate is currently at that stage. This allows skipping stages if interviews are recorded out of order.

### Scenario
1. Candidate status: `applied`
2. Recruiter accidentally schedules an onsite interview (skipping phone_screen and technical)
3. Interviewer records onsite as "passed"
4. Code calls `getNextStage('onsite')` → returns null
5. But if they had recorded a technical interview result for an `applied` candidate:
   - `getNextStage('technical')` → returns 'onsite'
   - Candidate jumps from `applied` directly to `onsite`!

### Impact
1. **Skipped interviews**: Candidates advance without completing required stages
2. **Hiring process violation**: Technical screening bypassed
3. **Legal/compliance risk**: Inconsistent interview process
4. **Quality degradation**: Unvetted candidates progress to offers

### Correct Implementation
```php
public function recordResult(int $interviewId, string $result, string $feedback): array
{
    $interview = Interview::findOrFail($interviewId);
    $candidate = $interview->candidate;

    // Verify candidate is at the right stage for this interview type
    $expectedStatus = $this->getExpectedStatusForInterview($interview->type);
    if ($candidate->status !== $expectedStatus) {
        return [
            'success' => false,
            'message' => "Candidate must be in {$expectedStatus} stage for this interview",
        ];
    }

    // ... rest of logic
}

private function getExpectedStatusForInterview(string $type): string
{
    return match ($type) {
        'phone_screen' => 'applied',
        'technical' => 'phone_screen',
        'onsite' => 'technical',
    };
}
```

### Severity: High
Allows bypassing the required interview stages in the hiring workflow.
