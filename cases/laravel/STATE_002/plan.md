# Subscription Lifecycle

## Overview

Manage subscription states from trial to active to cancelled.

## Requirements

1. Subscriptions start in trial state
2. Convert to active after trial ends (with valid payment)
3. Handle cancellation and expiration
4. Support pausing and resuming

## Valid States

- trial → active (payment confirmed)
- trial → cancelled (user cancels during trial)
- trial → expired (trial ends without payment)
- active → paused (user pauses)
- active → cancelled (user cancels)
- active → expired (payment failed)
- paused → active (user resumes)
- paused → cancelled (user cancels while paused)
