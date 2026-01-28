from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeliveryStatusService:
    """Service for managing order delivery status transitions."""
    
    DELIVERY_STATUSES = {
        'pending': 1,
        'processing': 2,
        'shipped': 3,
        'in_transit': 4,
        'out_for_delivery': 5,
        'delivered': 6,
        'returned': 7
    }
    
    VALID_TRANSITIONS = {
        'pending': ['processing'],
        'processing': ['shipped'],
        'shipped': ['in_transit'],
        'in_transit': ['out_for_delivery', 'delivered'],
        'out_for_delivery': ['delivered'],
        'delivered': ['returned'],
        'returned': []
    }
    
    def __init__(self):
        self.notification_service = None
    
    @transaction.atomic
    def update_delivery_status(self, order, new_status: str, tracking_info: Optional[Dict[str, Any]] = None) -> bool:
        """Update order delivery status with validation and notifications."""
        if not self._is_valid_status(new_status):
            raise ValidationError(f"Invalid delivery status: {new_status}")
        
        current_status = order.delivery_status
        
        if not self._validate_status_transition(current_status, new_status):
            raise ValidationError(f"Invalid status transition from {current_status} to {new_status}")
        
        previous_status = order.delivery_status
        order.delivery_status = new_status
        order.status_updated_at = datetime.now()
        
        if tracking_info:
            self._update_tracking_information(order, tracking_info)
        
        order.save()
        
        self._log_status_change(order, previous_status, new_status)
        self._send_status_notification(order, new_status)
        
        return True
    
    def _is_valid_status(self, status: str) -> bool:
        """Check if the provided status is valid."""
        return status in self.DELIVERY_STATUSES
    
    def _validate_status_transition(self, current_status: str, new_status: str) -> bool:
        """Validate if the status transition is allowed."""
        if current_status == new_status:
            return False
        
        allowed_transitions = self.VALID_TRANSITIONS.get(current_status, [])
        return new_status in allowed_transitions
    
    def _update_tracking_information(self, order, tracking_info: Dict[str, Any]) -> None:
        """Update order tracking information."""
        if 'tracking_number' in tracking_info:
            order.tracking_number = tracking_info['tracking_number']
        
        if 'carrier' in tracking_info:
            order.carrier = tracking_info['carrier']
        
        if 'estimated_delivery' in tracking_info:
            order.estimated_delivery_date = tracking_info['estimated_delivery']
    
    def _log_status_change(self, order, previous_status: str, new_status: str) -> None:
        """Log the status change for audit purposes."""
        logger.info(
            f"Order {order.id} status changed from {previous_status} to {new_status}"
        )
    
    def _send_status_notification(self, order, new_status: str) -> None:
        """Send notification to customer about status change."""
        if self.notification_service and order.customer:
            self.notification_service.send_delivery_update(
                order.customer.email,
                order.id,
                new_status
            )
    
    def get_status_order(self, status: str) -> int:
        """Get the numerical order of a delivery status."""
        return self.DELIVERY_STATUSES.get(status, 0)
    
    def can_transition_to(self, current_status: str, target_status: str) -> bool:
        """Check if transition from current to target status is valid."""
        return self._validate_status_transition(current_status, target_status)