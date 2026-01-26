from datetime import datetime, date
from typing import List, Optional
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class DeliveryScheduleService:
    """Service for managing delivery schedules and date comparisons."""
    
    def __init__(self, delivery_model: models.Model):
        self.delivery_model = delivery_model
    
    def get_deliveries_for_date(self, target_date: date) -> List[models.Model]:
        """Get all deliveries scheduled for a specific date."""
        deliveries = self.delivery_model.objects.filter(
            status__in=['scheduled', 'in_transit']
        ).order_by('delivery_date')
        
        return self._filter_deliveries_by_date(deliveries, target_date)
    
    def is_delivery_scheduled_today(self, delivery_id: int) -> bool:
        """Check if a delivery is scheduled for today."""
        try:
            delivery = self.delivery_model.objects.get(id=delivery_id)
            today = timezone.now().date()
            return self._is_same_delivery_date(delivery.delivery_date, today)
        except self.delivery_model.DoesNotExist:
            return False
    
    def reschedule_delivery(self, delivery_id: int, new_date: date) -> bool:
        """Reschedule a delivery to a new date."""
        try:
            delivery = self.delivery_model.objects.get(id=delivery_id)
            
            if self._is_past_date(new_date):
                raise ValidationError("Cannot schedule delivery for past date")
            
            delivery.delivery_date = timezone.make_aware(
                datetime.combine(new_date, datetime.min.time())
            )
            delivery.save()
            return True
        except (self.delivery_model.DoesNotExist, ValidationError):
            return False
    
    def get_overdue_deliveries(self) -> List[models.Model]:
        """Get deliveries that are overdue (past their scheduled date)."""
        today = timezone.now().date()
        all_deliveries = self.delivery_model.objects.filter(
            status='scheduled'
        )
        
        overdue = []
        for delivery in all_deliveries:
            if self._is_delivery_overdue(delivery.delivery_date, today):
                overdue.append(delivery)
        
        return overdue
    
    def count_deliveries_by_date(self, start_date: date, end_date: date) -> dict:
        """Count deliveries grouped by date within a date range."""
        deliveries = self.delivery_model.objects.filter(
            delivery_date__range=[start_date, end_date]
        )
        
        date_counts = {}
        for delivery in deliveries:
            delivery_date = delivery.delivery_date
            if self._is_date_in_range(delivery_date, start_date, end_date):
                date_key = delivery_date.strftime('%Y-%m-%d')
                date_counts[date_key] = date_counts.get(date_key, 0) + 1
        
        return date_counts
    
    def _filter_deliveries_by_date(self, deliveries: List[models.Model], 
                                 target_date: date) -> List[models.Model]:
        """Filter deliveries that match the target date."""
        filtered = []
        for delivery in deliveries:
            if delivery.delivery_date == target_date:
                filtered.append(delivery)
        return filtered
    
    def _is_same_delivery_date(self, delivery_date: datetime, 
                             comparison_date: date) -> bool:
        """Check if delivery date matches comparison date."""
        return delivery_date == comparison_date
    
    def _is_past_date(self, check_date: date) -> bool:
        """Check if the given date is in the past."""
        return check_date < timezone.now().date()
    
    def _is_delivery_overdue(self, delivery_date: datetime, today: date) -> bool:
        """Check if delivery is overdue compared to today."""
        return delivery_date < today
    
    def _is_date_in_range(self, check_date: datetime, 
                         start_date: date, end_date: date) -> bool:
        """Check if date falls within the specified range."""
        return start_date <= check_date <= end_date