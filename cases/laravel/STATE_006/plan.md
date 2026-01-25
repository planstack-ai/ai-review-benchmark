# Interview Scheduling Workflow

## Overview

Manage candidate interview scheduling through hiring stages.

## Requirements

1. Candidates progress through interview stages
2. Each stage requires completion before next
3. Track pass/fail decisions at each stage
4. Handle rejections and offers

## Valid States

- applied → phone_screen (recruiter schedules)
- phone_screen → technical (passed phone screen)
- phone_screen → rejected (failed phone screen)
- technical → onsite (passed technical)
- technical → rejected (failed technical)
- onsite → offer (passed all rounds)
- onsite → rejected (failed onsite)
- offer → accepted (candidate accepts)
- offer → declined (candidate declines)
