from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime
from django.db import connection, DatabaseError
from django.core.cache import cache
from django.conf import settings


class PerformanceAnalyticsService:
    MAX_RESULTS = 1000
    CACHE_TIMEOUT = 3600

    def __init__(self):
        self.cache_timeout = getattr(settings, 'ANALYTICS_CACHE_TIMEOUT', self.CACHE_TIMEOUT)

    def get_event_counts_by_date(self, start_date: datetime,
                                  end_date: datetime) -> List[Dict[str, Any]]:
        if not self._validate_date_range(start_date, end_date):
            raise ValueError("Invalid date range: start_date must be before end_date")

        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        DATE(ae.timestamp) as event_date,
                        ae.event_type,
                        COUNT(*) as event_count
                    FROM analytics_event ae
                    WHERE ae.timestamp BETWEEN %s AND %s
                    GROUP BY DATE(ae.timestamp), ae.event_type
                    ORDER BY event_date DESC, event_count DESC
                    LIMIT %s
                """
                cursor.execute(query, [start_date, end_date, self.MAX_RESULTS])
                return self._dictfetchall(cursor)

        except DatabaseError as e:
            raise RuntimeError(f"Database error while fetching event counts: {e}")

    def get_event_type_summary(self, start_date: datetime,
                               end_date: datetime) -> List[Dict[str, Any]]:
        if not self._validate_date_range(start_date, end_date):
            raise ValueError("Invalid date range: start_date must be before end_date")

        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        ae.event_type,
                        COUNT(*) as total_events,
                        COUNT(DISTINCT ae.user_id) as unique_users,
                        COUNT(DISTINCT ae.session_id) as unique_sessions,
                        MIN(ae.timestamp) as first_event,
                        MAX(ae.timestamp) as last_event
                    FROM analytics_event ae
                    WHERE ae.timestamp BETWEEN %s AND %s
                    GROUP BY ae.event_type
                    ORDER BY total_events DESC
                    LIMIT %s
                """
                cursor.execute(query, [start_date, end_date, self.MAX_RESULTS])
                return self._dictfetchall(cursor)

        except DatabaseError as e:
            raise RuntimeError(f"Database error while fetching event summary: {e}")

    def get_user_activity_summary(self, start_date: datetime,
                                  end_date: datetime) -> Dict[str, Any]:
        if not self._validate_date_range(start_date, end_date):
            raise ValueError("Invalid date range: start_date must be before end_date")

        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        COUNT(*) as total_events,
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(DISTINCT session_id) as unique_sessions,
                        COUNT(DISTINCT DATE(timestamp)) as active_days
                    FROM analytics_event
                    WHERE timestamp BETWEEN %s AND %s
                """
                cursor.execute(query, [start_date, end_date])
                result = self._dictfetchall(cursor)
                return result[0] if result else self._empty_activity_summary()

        except DatabaseError as e:
            raise RuntimeError(f"Database error while fetching activity summary: {e}")

    def get_conversion_funnel(self, start_date: datetime,
                              end_date: datetime) -> Dict[str, int]:
        if not self._validate_date_range(start_date, end_date):
            raise ValueError("Invalid date range: start_date must be before end_date")

        try:
            with connection.cursor() as cursor:
                query = """
                    SELECT
                        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as page_viewers,
                        COUNT(DISTINCT CASE WHEN event_type = 'click' THEN user_id END) as clickers,
                        COUNT(DISTINCT CASE WHEN event_type = 'form_submit' THEN user_id END) as form_submitters,
                        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as purchasers
                    FROM analytics_event
                    WHERE timestamp BETWEEN %s AND %s
                        AND user_id IS NOT NULL
                """
                cursor.execute(query, [start_date, end_date])
                result = self._dictfetchall(cursor)
                return result[0] if result else self._empty_funnel()

        except DatabaseError as e:
            raise RuntimeError(f"Database error while calculating conversion funnel: {e}")

    def _validate_date_range(self, start_date: datetime, end_date: datetime) -> bool:
        if start_date is None or end_date is None:
            return False
        return start_date <= end_date

    def _dictfetchall(self, cursor) -> List[Dict[str, Any]]:
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def _empty_activity_summary(self) -> Dict[str, Any]:
        return {
            'total_events': 0,
            'unique_users': 0,
            'unique_sessions': 0,
            'active_days': 0
        }

    def _empty_funnel(self) -> Dict[str, int]:
        return {
            'page_viewers': 0,
            'clickers': 0,
            'form_submitters': 0,
            'purchasers': 0
        }
