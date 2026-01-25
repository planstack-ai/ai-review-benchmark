# Booking Time Slot Management

## Overview

Manage appointment booking time slots.

## Requirements

1. Slots are defined per day with start/end times
2. Prevent double booking
3. Consider buffer time between appointments
4. Handle timezone for display vs storage

## Business Rules

- Slots stored in business timezone (Asia/Tokyo)
- Buffer time: 15 minutes between appointments
- Cannot book past time slots
