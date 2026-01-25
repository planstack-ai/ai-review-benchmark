from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta


class PerformanceAnalyticsService:
    
    def __init__(self):
        self.cache_timeout = getattr(settings, 'ANALYTICS_CACHE_TIMEOUT', 3600)
        self.batch_size = 10000
    
    def get_user_engagement_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        cache_key = f"engagement_metrics_{start_date.date()}_{end_date.date()}"
        cached_result = cache.get(cache_key)
        
        if cached_result:
            return cached_result
        
        with connection.cursor() as cursor:
            query = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(DISTINCT user_id) as active_users,
                    COUNT(*) as total_actions,
                    AVG(session_duration) as avg_session_duration,
                    SUM(CASE WHEN action_type = 'purchase' THEN 1 ELSE 0 END) as purchases
                FROM user_activities ua
                LEFT JOIN user_sessions us ON ua.session_id = us.id
                WHERE ua.created_at BETWEEN %s AND %s
                    AND ua.user_id IS NOT NULL
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """
            cursor.execute(query, [start_date, end_date])
            results = self._dictfetchall(cursor)
        
        processed_metrics = self._process_engagement_data(results)
        cache.set(cache_key, processed_metrics, self.cache_timeout)
        
        return processed_metrics
    
    def get_revenue_breakdown_by_category(self, user_segment: str, days: int = 30) -> List[Dict[str, Any]]:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        segment_filter = self._build_segment_filter(user_segment)
        
        with connection.cursor() as cursor:
            query = f"""
                SELECT 
                    pc.name as category_name,
                    pc.id as category_id,
                    COUNT(DISTINCT o.id) as order_count,
                    SUM(oi.quantity * oi.unit_price) as total_revenue,
                    AVG(oi.quantity * oi.unit_price) as avg_order_value,
                    COUNT(DISTINCT o.user_id) as unique_customers
                FROM orders o
                INNER JOIN order_items oi ON o.id = oi.order_id
                INNER JOIN products p ON oi.product_id = p.id
                INNER JOIN product_categories pc ON p.category_id = pc.id
                INNER JOIN users u ON o.user_id = u.id
                WHERE o.created_at BETWEEN %s AND %s
                    AND o.status = 'completed'
                    {segment_filter}
                GROUP BY pc.id, pc.name
                HAVING total_revenue > 0
                ORDER BY total_revenue DESC
            """
            cursor.execute(query, [start_date, end_date])
            return self._dictfetchall(cursor)
    
    def calculate_customer_lifetime_value(self, cohort_months: int = 12) -> Dict[str, Decimal]:
        with connection.cursor() as cursor:
            query = """
                WITH customer_cohorts AS (
                    SELECT 
                        user_id,
                        DATE_TRUNC('month', MIN(created_at)) as cohort_month,
                        SUM(total_amount) as total_spent,
                        COUNT(*) as order_count,
                        MAX(created_at) as last_order_date
                    FROM orders
                    WHERE status = 'completed'
                        AND created_at >= NOW() - INTERVAL '%s months'
                    GROUP BY user_id
                ),
                cohort_analysis AS (
                    SELECT 
                        cohort_month,
                        COUNT(DISTINCT user_id) as cohort_size,
                        AVG(total_spent) as avg_revenue_per_customer,
                        AVG(order_count) as avg_orders_per_customer,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_spent) as median_clv
                    FROM customer_cohorts
                    GROUP BY cohort_month
                )
                SELECT 
                    cohort_month,
                    cohort_size,
                    avg_revenue_per_customer,
                    avg_orders_per_customer,
                    median_clv
                FROM cohort_analysis
                ORDER BY cohort_month DESC
            """
            cursor.execute(query, [cohort_months])
            results = self._dictfetchall(cursor)
        
        return self._aggregate_clv_metrics(results)
    
    def _dictfetchall(self, cursor) -> List[Dict[str, Any]]:
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def _process_engagement_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not raw_data:
            return {'daily_metrics': [], 'summary': {}}
        
        total_users = sum(row['active_users'] for row in raw_data)
        total_actions = sum(row['total_actions'] for row in raw_data)
        total_purchases = sum(row['purchases'] for row in raw_data)
        
        return {
            'daily_metrics': raw_data,
            'summary': {
                'total_active_users': total_users,
                'total_actions': total_actions,
                'total_purchases': total_purchases,
                'conversion_rate': (total_purchases / total_actions * 100) if total_actions > 0 else 0
            }
        }
    
    def _build_segment_filter(self, segment: str) -> str:
        segment_conditions = {
            'premium': "AND u.subscription_tier = 'premium'",
            'new': "AND u.created_at >= NOW() - INTERVAL '30 days'",
            'returning': "AND u.created_at < NOW() - INTERVAL '30 days'",
            'high_value': "AND u.total_spent > 1000"
        }
        return segment_conditions.get(segment, "")
    
    def _aggregate_clv_metrics(self, cohort_data: List[Dict[str, Any]]) -> Dict[str, Decimal]:
        if not cohort_data:
            return {}
        
        total_customers = sum(row['cohort_size'] for row in cohort_data)
        weighted_avg_clv = sum(
            row['avg_revenue_per_customer'] * row['cohort_size'] 
            for row in cohort_data
        ) / total_customers if total_customers > 0 else Decimal('0')
        
        return {
            'overall_clv': Decimal(str(weighted_avg_clv)).quantize(Decimal('0.01')),
            'total_customers_analyzed': total_customers,
            'cohort_count': len(cohort_data)
        }