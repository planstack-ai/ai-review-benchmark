from enum import Enum
from typing import Dict, List, Optional, Set
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime


class ReviewState(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class CodeReviewStateMachine:
    
    def __init__(self, review_instance):
        self.review = review_instance
        self._state_transitions = self._build_transition_map()
        self._state_handlers = self._build_handler_map()
    
    def _build_transition_map(self) -> Dict[ReviewState, Set[ReviewState]]:
        return {
            ReviewState.PENDING: {ReviewState.IN_PROGRESS, ReviewState.ARCHIVED},
            ReviewState.IN_PROGRESS: {ReviewState.REVIEWED, ReviewState.PENDING, ReviewState.ARCHIVED},
            ReviewState.REVIEWED: {ReviewState.APPROVED, ReviewState.REJECTED, ReviewState.IN_PROGRESS},
            ReviewState.APPROVED: {ReviewState.ARCHIVED},
            ReviewState.REJECTED: {ReviewState.IN_PROGRESS, ReviewState.ARCHIVED},
            ReviewState.ARCHIVED: set()
        }
    
    def _build_handler_map(self) -> Dict[ReviewState, str]:
        return {
            ReviewState.PENDING: "_handle_pending_state",
            ReviewState.IN_PROGRESS: "_handle_in_progress_state",
            ReviewState.REVIEWED: "_handle_reviewed_state",
            ReviewState.APPROVED: "_handle_approved_state",
            ReviewState.REJECTED: "_handle_rejected_state",
            ReviewState.ARCHIVED: "_handle_archived_state"
        }
    
    def transition_to(self, target_state: ReviewState, user_id: int, notes: Optional[str] = None) -> bool:
        current_state = ReviewState(self.review.status)
        
        if not self._is_valid_transition(current_state, target_state):
            raise ValidationError(f"Invalid transition from {current_state.value} to {target_state.value}")
        
        with transaction.atomic():
            self._execute_state_handler(target_state, user_id, notes)
            self.review.status = target_state.value
            self.review.updated_at = timezone.now()
            self.review.save()
            
        return True
    
    def _is_valid_transition(self, current_state: ReviewState, target_state: ReviewState) -> bool:
        allowed_transitions = self._state_transitions.get(current_state, set())
        return target_state in allowed_transitions
    
    def _execute_state_handler(self, state: ReviewState, user_id: int, notes: Optional[str]) -> None:
        handler_name = self._state_handlers.get(state)
        if handler_name:
            handler = getattr(self, handler_name)
            handler(user_id, notes)
    
    def _handle_pending_state(self, user_id: int, notes: Optional[str]) -> None:
        self.review.assigned_reviewer = None
        self.review.review_started_at = None
    
    def _handle_in_progress_state(self, user_id: int, notes: Optional[str]) -> None:
        self.review.assigned_reviewer_id = user_id
        self.review.review_started_at = timezone.now()
    
    def _handle_reviewed_state(self, user_id: int, notes: Optional[str]) -> None:
        self.review.reviewed_by_id = user_id
        self.review.reviewed_at = timezone.now()
        if notes:
            self.review.review_notes = notes
    
    def _handle_approved_state(self, user_id: int, notes: Optional[str]) -> None:
        self.review.approved_by_id = user_id
        self.review.approved_at = timezone.now()
        self._notify_approval()
    
    def _handle_rejected_state(self, user_id: int, notes: Optional[str]) -> None:
        self.review.rejected_by_id = user_id
        self.review.rejected_at = timezone.now()
        if notes:
            self.review.rejection_reason = notes
    
    def _handle_archived_state(self, user_id: int, notes: Optional[str]) -> None:
        self.review.archived_by_id = user_id
        self.review.archived_at = timezone.now()
    
    def _notify_approval(self) -> None:
        from .tasks import send_approval_notification
        send_approval_notification.delay(self.review.id)
    
    def get_available_transitions(self) -> List[ReviewState]:
        current_state = ReviewState(self.review.status)
        return list(self._state_transitions.get(current_state, set()))