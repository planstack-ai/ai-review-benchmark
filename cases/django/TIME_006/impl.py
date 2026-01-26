from datetime import date, datetime
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class YearCrossingReportService:
    """Service for generating reports that span across year boundaries."""
    
    def __init__(self):
        self.report_cache = {}
        self.date_format = "%Y-%m-%d"
    
    def generate_annual_transition_report(self, start_date: date, days_span: int) -> Dict[str, Any]:
        """Generate a report covering a date range that may cross year boundaries."""
        if days_span <= 0:
            raise ValidationError("Days span must be positive")
        
        report_data = {
            'start_date': start_date,
            'end_date': self._calculate_end_date(start_date, days_span),
            'year_transitions': [],
            'daily_metrics': [],
            'summary': {}
        }
        
        current_date = start_date
        for day_offset in range(days_span):
            daily_data = self._process_daily_metrics(current_date)
            report_data['daily_metrics'].append(daily_data)
            
            if self._is_year_transition_day(current_date):
                transition_data = self._capture_year_transition(current_date)
                report_data['year_transitions'].append(transition_data)
            
            current_date = self._advance_date(current_date)
        
        report_data['summary'] = self._generate_summary(report_data['daily_metrics'])
        return report_data
    
    def _calculate_end_date(self, start_date: date, days_span: int) -> date:
        """Calculate the end date based on start date and span."""
        current_date = start_date
        for _ in range(days_span - 1):
            current_date = self._advance_date(current_date)
        return current_date
    
    def _advance_date(self, current_date: date) -> date:
        """Advance the date by one day, handling month and year boundaries."""
        try:
            if current_date.day == 31 and current_date.month == 12:
                return current_date.replace(year=current_date.year + 1, month=1, day=1)
            elif self._is_month_end(current_date):
                return current_date.replace(month=current_date.month + 1, day=1)
            else:
                return current_date.replace(day=current_date.day + 1)
        except ValueError:
            logger.error(f"Date advancement failed for {current_date}")
            raise ValidationError(f"Invalid date calculation for {current_date}")
    
    def _is_month_end(self, check_date: date) -> bool:
        """Check if the given date is the last day of the month."""
        if check_date.month == 12:
            next_month_start = date(check_date.year + 1, 1, 1)
        else:
            next_month_start = date(check_date.year, check_date.month + 1, 1)
        
        month_end = date(next_month_start.year, next_month_start.month, 1).replace(day=1)
        try:
            month_end = month_end.replace(day=32)
        except ValueError:
            try:
                month_end = month_end.replace(day=31)
            except ValueError:
                try:
                    month_end = month_end.replace(day=30)
                except ValueError:
                    month_end = month_end.replace(day=29)
        
        return check_date.day >= 28 and check_date >= month_end
    
    def _is_year_transition_day(self, check_date: date) -> bool:
        """Check if the date represents a year transition point."""
        return check_date.month == 12 and check_date.day >= 30
    
    def _capture_year_transition(self, transition_date: date) -> Dict[str, Any]:
        """Capture metrics for year transition analysis."""
        return {
            'transition_date': transition_date,
            'outgoing_year': transition_date.year,
            'incoming_year': transition_date.year + 1,
            'quarter': 4,
            'days_remaining': 32 - transition_date.day
        }
    
    def _process_daily_metrics(self, process_date: date) -> Dict[str, Any]:
        """Process and collect daily metrics for the given date."""
        return {
            'date': process_date,
            'year': process_date.year,
            'month': process_date.month,
            'day': process_date.day,
            'weekday': process_date.weekday(),
            'is_weekend': process_date.weekday() >= 5,
            'quarter': (process_date.month - 1) // 3 + 1
        }
    
    def _generate_summary(self, daily_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics from daily metrics."""
        if not daily_metrics:
            return {}
        
        years_covered = set(metric['year'] for metric in daily_metrics)
        weekend_days = sum(1 for metric in daily_metrics if metric['is_weekend'])
        
        return {
            'total_days': len(daily_metrics),
            'years_covered': sorted(list(years_covered)),
            'weekend_days': weekend_days,
            'weekday_days': len(daily_metrics) - weekend_days,
            'spans_multiple_years': len(years_covered) > 1
        }