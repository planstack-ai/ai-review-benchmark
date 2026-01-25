# Expected Critique

## Bug: Ticket Assignment Without State Check

### Location
`assignToAgent()` method:
```php
public function assignToAgent(int $ticketId, User $agent): array
{
    $ticket = Ticket::findOrFail($ticketId);

    // No state check!
    $ticket->update([
        'assigned_agent_id' => $agent->id,
        'status' => 'in_progress',
    ]);
```

### Problem
The method assigns an agent and forces status to `in_progress` without checking the current ticket state. This allows:
- Resolved tickets to become in_progress again (bypassing reopen workflow)
- Closed tickets (spam/duplicates) to become active
- Escalated tickets to lose escalation status

### Impact
1. **Workflow bypass**: Can reopen resolved/closed tickets without proper channel
2. **Escalation lost**: Escalated tickets can be de-escalated by assignment
3. **Metrics corruption**: Resolution times and ticket lifecycle tracking broken
4. **Customer confusion**: Closed tickets suddenly become active

### Secondary Issue
`customerReply()` allows replying to closed tickets and changes them to in_progress, when closed tickets (spam/duplicate) should not be reopenable.

### Correct Implementation
```php
public function assignToAgent(int $ticketId, User $agent): array
{
    $ticket = Ticket::findOrFail($ticketId);

    $assignableStates = ['open', 'escalated', 'reopened'];
    if (!in_array($ticket->status, $assignableStates)) {
        return [
            'success' => false,
            'message' => 'Ticket cannot be assigned in current state',
        ];
    }

    $ticket->update([
        'assigned_agent_id' => $agent->id,
        'status' => 'in_progress',
    ]);

    return ['success' => true, 'ticket' => $ticket];
}
```

### Severity: Medium
Breaks ticket workflow integrity and allows bypassing proper state transitions.
