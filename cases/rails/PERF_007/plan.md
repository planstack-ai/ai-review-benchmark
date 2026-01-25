# Project Analytics Dashboard

## Overview
Build an analytics service that generates reports for a user's projects, including team performance metrics, completion rates, and recent activity. This service will be used frequently on dashboards and may operate on users with many projects.

## Requirements
1. Generate comprehensive project reports with summaries, team performance, and completion metrics
2. Export detailed project data including task counts, team sizes, and recent comments
3. Calculate productivity scores per project with completion rates and member efficiency
4. Track recent activity across all projects

## Constraints
1. A user may have many projects (potentially hundreds)
2. Each project may have many tasks, team members, and comments
3. The service is called frequently for dashboard rendering
4. Reports must be generated within acceptable response times
5. Memory usage should remain predictable regardless of data size

## References
See context.md for Project, Task, TeamMember, and Comment model definitions.
