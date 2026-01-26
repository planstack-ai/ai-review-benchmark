from decimal import Decimal
from typing import List, Dict, Optional, Tuple
from django.db import connection
from django.core.exceptions import ValidationError


class PerformanceAnalyticsService:
    
    def __init__(self):
        self.connection = connection
    
    def get_user_performance_metrics(self, user_ids: List[int], date_range: Tuple[str, str]) -> List[Dict]:
        if not user_ids or len(user_ids) > 1000:
            raise ValidationError("User IDs list must contain 1-1000 items")
        
        start_date, end_date = date_range
        placeholders = ','.join(['%s'] * len(user_ids))
        
        query = f"""
            SELECT 
                u.id as user_id,
                u.username,
                u.email,
                COUNT(DISTINCT o.id) as total_orders,
                COALESCE(SUM(oi.quantity * oi.unit_price), 0) as total_revenue,
                AVG(r.rating) as avg_rating,
                COUNT(DISTINCT r.id) as review_count,
                MAX(o.created_at) as last_order_date
            FROM auth_user u
            LEFT JOIN orders_order o ON u.id = o.user_id 
                AND o.created_at BETWEEN %s AND %s
                AND o.status = 'completed'
            LEFT JOIN orders_orderitem oi ON o.id = oi.order_id
            LEFT JOIN reviews_review r ON u.id = r.user_id 
                AND r.created_at BETWEEN %s AND %s
            WHERE u.id IN ({placeholders})
                AND u.is_active = true
            GROUP BY u.id, u.username, u.email
            ORDER BY total_revenue DESC, total_orders DESC
        """
        
        params = [start_date, end_date, start_date, end_date] + user_ids
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return self._process_performance_results(results)
    
    def get_product_sales_analysis(self, category_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        category_filter = "AND p.category_id = %s" if category_id else ""
        category_params = [category_id] if category_id else []
        
        query = f"""
            SELECT 
                p.id as product_id,
                p.name as product_name,
                p.sku,
                c.name as category_name,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.quantity) as total_quantity_sold,
                SUM(oi.quantity * oi.unit_price) as total_sales,
                AVG(oi.unit_price) as avg_unit_price,
                MIN(oi.unit_price) as min_price,
                MAX(oi.unit_price) as max_price,
                COALESCE(AVG(pr.rating), 0) as avg_product_rating
            FROM products_product p
            INNER JOIN products_category c ON p.category_id = c.id
            LEFT JOIN orders_orderitem oi ON p.id = oi.product_id
            LEFT JOIN orders_order o ON oi.order_id = o.id AND o.status = 'completed'
            LEFT JOIN products_productreview pr ON p.id = pr.product_id
            WHERE p.is_active = true {category_filter}
            GROUP BY p.id, p.name, p.sku, c.name
            HAVING COUNT(DISTINCT oi.order_id) > 0
            ORDER BY total_sales DESC, total_quantity_sold DESC
            LIMIT %s
        """
        
        params = category_params + [limit]
        
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return self._calculate_sales_metrics(results)
    
    def _process_performance_results(self, results: List[Dict]) -> List[Dict]:
        processed_results = []
        
        for result in results:
            total_revenue = Decimal(str(result.get('total_revenue', 0)))
            total_orders = result.get('total_orders', 0)
            avg_rating = result.get('avg_rating')
            
            processed_result = {
                'user_id': result['user_id'],
                'username': result['username'],
                'email': result['email'],
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'avg_order_value': total_revenue / total_orders if total_orders > 0 else Decimal('0'),
                'avg_rating': round(float(avg_rating), 2) if avg_rating else None,
                'review_count': result.get('review_count', 0),
                'last_order_date': result.get('last_order_date'),
                'performance_tier': self._calculate_performance_tier(total_revenue, total_orders)
            }
            processed_results.append(processed_result)
        
        return processed_results
    
    def _calculate_sales_metrics(self, results: List[Dict]) -> List[Dict]:
        for result in results:
            total_sales = Decimal(str(result.get('total_sales', 0)))
            total_quantity = result.get('total_quantity_sold', 0)
            order_count = result.get('order_count', 0)
            
            result['total_sales'] = total_sales
            result['avg_quantity_per_order'] = total_quantity / order_count if order_count > 0 else 0
            result['revenue_per_unit'] = total_sales / total_quantity if total_quantity > 0 else Decimal('0')
            result['avg_product_rating'] = round(float(result.get('avg_product_rating', 0)), 2)
        
        return results
    
    def _calculate_performance_tier(self, revenue: Decimal, orders: int) -> str:
        if revenue >= Decimal('10000') and orders >= 50:
            return 'premium'
        elif revenue >= Decimal('5000') and orders >= 20:
            return 'gold'
        elif revenue >= Decimal('1000') and orders >= 5:
            return 'silver'
        else:
            return 'bronze'