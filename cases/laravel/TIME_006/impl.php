<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Event;
use App\Models\EventOccurrence;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;

class EventSchedulingService
{
    public function createEvent(
        int $userId,
        string $title,
        string $startTime,
        string $endTime,
        string $timezone,
        bool $isRecurring = false,
        ?string $recurrenceEnd = null
    ): array {
        $start = Carbon::parse($startTime, $timezone)->utc();
        $end = Carbon::parse($endTime, $timezone)->utc();

        $event = Event::create([
            'user_id' => $userId,
            'title' => $title,
            'start_time' => $start,
            'end_time' => $end,
            'timezone' => $timezone,
            'is_recurring' => $isRecurring,
            'recurrence_pattern' => $isRecurring ? 'weekly' : null,
            'recurrence_end' => $recurrenceEnd,
        ]);

        if ($isRecurring) {
            $this->generateOccurrences($event);
        }

        return ['success' => true, 'event' => $event];
    }

    public function generateOccurrences(Event $event): void
    {
        if (!$event->is_recurring) {
            return;
        }

        $start = Carbon::parse($event->start_time);
        $end = Carbon::parse($event->end_time);
        $duration = $start->diffInMinutes($end);

        $recurrenceEnd = $event->recurrence_end
            ? Carbon::parse($event->recurrence_end)
            : now()->addMonths(3);

        $currentStart = $start->copy();

        while ($currentStart->lte($recurrenceEnd)) {
            EventOccurrence::create([
                'event_id' => $event->id,
                'start_time' => $currentStart,
                'end_time' => $currentStart->copy()->addMinutes($duration),
            ]);

            // BUG: Adds exactly 7 days (168 hours) instead of "next week same time"
            // During DST transitions, this shifts the wall clock time
            // Example: 10:00 AM becomes 9:00 AM or 11:00 AM after DST change
            $currentStart->addDays(7);
        }
    }

    public function getOccurrencesInRange(int $eventId, string $startDate, string $endDate): Collection
    {
        return EventOccurrence::where('event_id', $eventId)
            ->whereBetween('start_time', [$startDate, $endDate])
            ->orderBy('start_time')
            ->get();
    }

    public function getUserEventsForDay(int $userId, string $date, string $timezone): Collection
    {
        $dayStart = Carbon::parse($date, $timezone)->startOfDay()->utc();
        $dayEnd = Carbon::parse($date, $timezone)->endOfDay()->utc();

        $events = Event::where('user_id', $userId)
            ->where(function ($query) use ($dayStart, $dayEnd) {
                $query->where('is_recurring', false)
                    ->whereBetween('start_time', [$dayStart, $dayEnd]);
            })
            ->orWhere(function ($query) use ($userId) {
                $query->where('user_id', $userId)
                    ->where('is_recurring', true);
            })
            ->get();

        // For recurring events, get occurrences
        $occurrences = EventOccurrence::whereIn('event_id', $events->where('is_recurring', true)->pluck('id'))
            ->whereBetween('start_time', [$dayStart, $dayEnd])
            ->get();

        return $events->where('is_recurring', false)->merge(
            $occurrences->map(fn($o) => $o->event)
        );
    }
}
