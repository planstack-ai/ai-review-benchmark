<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Ticket;
use App\Models\TicketReply;
use App\Models\User;

class TicketService
{
    public function assignToAgent(int $ticketId, User $agent): array
    {
        $ticket = Ticket::findOrFail($ticketId);

        // BUG: Allows assigning agent to resolved/closed tickets
        // Should only assign to open, in_progress, escalated, reopened
        $ticket->update([
            'assigned_agent_id' => $agent->id,
            'status' => 'in_progress',
        ]);

        return ['success' => true, 'ticket' => $ticket];
    }

    public function requestCustomerInfo(int $ticketId, User $agent, string $question): array
    {
        $ticket = Ticket::findOrFail($ticketId);

        if ($ticket->status !== 'in_progress') {
            return [
                'success' => false,
                'message' => 'Ticket must be in progress',
            ];
        }

        TicketReply::create([
            'ticket_id' => $ticketId,
            'user_id' => $agent->id,
            'message' => $question,
        ]);

        $ticket->update(['status' => 'waiting_customer']);

        return ['success' => true, 'ticket' => $ticket];
    }

    public function customerReply(int $ticketId, User $customer, string $message): array
    {
        $ticket = Ticket::findOrFail($ticketId);

        if ($ticket->customer_id !== $customer->id) {
            return [
                'success' => false,
                'message' => 'Only ticket owner can reply',
            ];
        }

        TicketReply::create([
            'ticket_id' => $ticketId,
            'user_id' => $customer->id,
            'message' => $message,
        ]);

        // BUG: Changes status to in_progress even if ticket was resolved/closed
        // Should only change from waiting_customer to in_progress
        if (in_array($ticket->status, ['waiting_customer', 'resolved', 'closed'])) {
            $newStatus = $ticket->status === 'resolved' ? 'reopened' : 'in_progress';
            $ticket->update(['status' => $newStatus]);
        }

        return ['success' => true, 'ticket' => $ticket];
    }

    public function resolve(int $ticketId, User $agent, string $resolution): array
    {
        $ticket = Ticket::findOrFail($ticketId);

        if ($ticket->status !== 'in_progress') {
            return [
                'success' => false,
                'message' => 'Ticket must be in progress to resolve',
            ];
        }

        TicketReply::create([
            'ticket_id' => $ticketId,
            'user_id' => $agent->id,
            'message' => "Resolution: {$resolution}",
            'is_internal' => false,
        ]);

        $ticket->update([
            'status' => 'resolved',
            'resolved_at' => now(),
        ]);

        return ['success' => true, 'ticket' => $ticket];
    }

    public function escalate(int $ticketId, User $agent, string $reason): array
    {
        $ticket = Ticket::findOrFail($ticketId);

        if ($ticket->status !== 'in_progress') {
            return [
                'success' => false,
                'message' => 'Ticket must be in progress to escalate',
            ];
        }

        TicketReply::create([
            'ticket_id' => $ticketId,
            'user_id' => $agent->id,
            'message' => "Escalation reason: {$reason}",
            'is_internal' => true,
        ]);

        $ticket->update([
            'status' => 'escalated',
            'assigned_agent_id' => null,
        ]);

        return ['success' => true, 'ticket' => $ticket];
    }
}
