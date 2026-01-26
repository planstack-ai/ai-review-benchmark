# Existing Codebase

## Schema

```sql
CREATE TABLE workflow_process (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    current_state VARCHAR(50) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE workflow_transition (
    id SERIAL PRIMARY KEY,
    process_id INTEGER REFERENCES workflow_process(id) ON DELETE CASCADE,
    from_state VARCHAR(50) NOT NULL,
    to_state VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id INTEGER,
    notes TEXT
);

CREATE INDEX idx_process_state ON workflow_process(current_state);
CREATE INDEX idx_transition_process ON workflow_transition(process_id);
```

## Models

```python
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from typing import Dict, List, Optional, Set
from enum import Enum

User = get_user_model()


class WorkflowState(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SUBMITTED = 'submitted', 'Submitted'
    UNDER_REVIEW = 'under_review', 'Under Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class WorkflowAction(models.TextChoices):
    SUBMIT = 'submit', 'Submit'
    START_REVIEW = 'start_review', 'Start Review'
    APPROVE = 'approve', 'Approve'
    REJECT = 'reject', 'Reject'
    PUBLISH = 'publish', 'Publish'
    ARCHIVE = 'archive', 'Archive'
    REOPEN = 'reopen', 'Reopen'


class ProcessQuerySet(models.QuerySet):
    def in_state(self, state: str) -> 'ProcessQuerySet':
        return self.filter(current_state=state)
    
    def pending_review(self) -> 'ProcessQuerySet':
        return self.filter(current_state__in=[
            WorkflowState.SUBMITTED,
            WorkflowState.UNDER_REVIEW
        ])
    
    def active(self) -> 'ProcessQuerySet':
        return self.exclude(current_state=WorkflowState.ARCHIVED)


class ProcessManager(models.Manager):
    def get_queryset(self) -> ProcessQuerySet:
        return ProcessQuerySet(self.model, using=self._db)
    
    def in_state(self, state: str) -> ProcessQuerySet:
        return self.get_queryset().in_state(state)


class Process(models.Model):
    name = models.CharField(max_length=255)
    current_state = models.CharField(
        max_length=50,
        choices=WorkflowState.choices,
        default=WorkflowState.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)
    
    objects = ProcessManager()
    
    class Meta:
        db_table = 'workflow_process'
    
    def get_available_actions(self) -> List[str]:
        """Returns list of valid actions from current state."""
        return list(self._get_valid_transitions().keys())
    
    def get_next_state(self, action: str) -> Optional[str]:
        """Returns the next state for given action, or None if invalid."""
        return self._get_valid_transitions().get(action)
    
    def _get_valid_transitions(self) -> Dict[str, str]:
        """Internal method to get valid state transitions."""
        transitions = {
            WorkflowState.DRAFT: {
                WorkflowAction.SUBMIT: WorkflowState.SUBMITTED,
                WorkflowAction.ARCHIVE: WorkflowState.ARCHIVED,
            },
            WorkflowState.SUBMITTED: {
                WorkflowAction.START_REVIEW: WorkflowState.UNDER_REVIEW,
                WorkflowAction.ARCHIVE: WorkflowState.ARCHIVED,
            },
            WorkflowState.UNDER_REVIEW: {
                WorkflowAction.APPROVE: WorkflowState.APPROVED,
                WorkflowAction.REJECT: WorkflowState.REJECTED,
            },
            WorkflowState.APPROVED: {
                WorkflowAction.PUBLISH: WorkflowState.PUBLISHED,
                WorkflowAction.ARCHIVE: WorkflowState.ARCHIVED,
            },
            WorkflowState.REJECTED: {
                WorkflowAction.REOPEN: WorkflowState.DRAFT,
                WorkflowAction.ARCHIVE: WorkflowState.ARCHIVED,
            },
            WorkflowState.PUBLISHED: {
                WorkflowAction.ARCHIVE: WorkflowState.ARCHIVED,
            },
            WorkflowState.ARCHIVED: {},
        }
        return transitions.get(self.current_state, {})


class Transition(models.Model):
    process = models.ForeignKey(
        Process,
        on_delete=models.CASCADE,
        related_name='transitions'
    )
    from_state = models.CharField(max_length=50, choices=WorkflowState.choices)
    to_state = models.CharField(max_length=50, choices=WorkflowState.choices)
    action = models.CharField(max_length=100, choices=WorkflowAction.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'workflow_transition'
        ordering = ['-timestamp']
```