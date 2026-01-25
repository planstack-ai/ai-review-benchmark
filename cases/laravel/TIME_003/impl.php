<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Booking;
use App\Models\TimeSlot;
use Illuminate\Support\Carbon;

class BookingService
{
    private const BUSINESS_TIMEZONE = 'Asia/Tokyo';
    private const BUFFER_MINUTES = 15;

    public function getAvailableSlots(string $date): array
    {
        $slots = TimeSlot::where('date', $date)
            ->where('available', true)
            ->whereDoesntHave('bookings', function ($query) {
                $query->where('status', 'confirmed');
            })
            ->get();

        // BUG: Filters past slots using server time (UTC) instead of business timezone
        // A slot at 10:00 Tokyo might be filtered out incorrectly
        return $slots->filter(function ($slot) {
            $slotDateTime = Carbon::parse($slot->date . ' ' . $slot->start_time);

            return $slotDateTime->isFuture();
        })->values()->all();
    }

    public function bookSlot(int $userId, int $slotId): array
    {
        $slot = TimeSlot::findOrFail($slotId);

        if (!$slot->available) {
            return ['success' => false, 'message' => 'Slot is not available'];
        }

        $existingBooking = Booking::where('time_slot_id', $slotId)
            ->where('status', 'confirmed')
            ->exists();

        if ($existingBooking) {
            return ['success' => false, 'message' => 'Slot is already booked'];
        }

        // BUG: Past slot check uses server time without timezone consideration
        $slotDateTime = Carbon::parse($slot->date . ' ' . $slot->start_time);
        if ($slotDateTime->isPast()) {
            return ['success' => false, 'message' => 'Cannot book past time slots'];
        }

        $booking = Booking::create([
            'user_id' => $userId,
            'time_slot_id' => $slotId,
            'status' => 'confirmed',
        ]);

        return ['success' => true, 'booking' => $booking];
    }

    public function cancelBooking(int $bookingId, int $userId): array
    {
        $booking = Booking::where('id', $bookingId)
            ->where('user_id', $userId)
            ->firstOrFail();

        if ($booking->status === 'cancelled') {
            return ['success' => false, 'message' => 'Booking already cancelled'];
        }

        $booking->update(['status' => 'cancelled']);

        return ['success' => true];
    }

    public function checkBufferConflict(int $slotId): bool
    {
        $slot = TimeSlot::findOrFail($slotId);

        $slotStart = Carbon::parse($slot->date . ' ' . $slot->start_time);
        $slotEnd = Carbon::parse($slot->date . ' ' . $slot->end_time);

        // Check if adjacent slots have bookings within buffer time
        $adjacentBookings = Booking::whereHas('timeSlot', function ($query) use ($slot, $slotStart, $slotEnd) {
            $query->where('date', $slot->date)
                ->where(function ($q) use ($slotStart, $slotEnd) {
                    // Slot ends within buffer of our start
                    $q->whereRaw("TIME(end_time) > ?", [$slotStart->subMinutes(self::BUFFER_MINUTES)->format('H:i:s')])
                        ->whereRaw("TIME(end_time) <= ?", [$slotStart->format('H:i:s')]);
                })
                ->orWhere(function ($q) use ($slotEnd) {
                    // Slot starts within buffer of our end
                    $q->whereRaw("TIME(start_time) >= ?", [$slotEnd->format('H:i:s')])
                        ->whereRaw("TIME(start_time) < ?", [$slotEnd->addMinutes(self::BUFFER_MINUTES)->format('H:i:s')]);
                });
        })
            ->where('status', 'confirmed')
            ->exists();

        return $adjacentBookings;
    }
}
