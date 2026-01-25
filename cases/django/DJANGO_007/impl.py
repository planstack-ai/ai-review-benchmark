from decimal import Decimal
from typing import List, Dict, Optional, Any
from django.db import connection, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class OrderAnalyticsService:
    """Service for analyzing order data and generating reports."""
    
    def __init__(self):
        self.connection = connection
    
    def get_order_summary(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve comprehensive order summary including items and totals."""
        if not self._validate_order_id(order_id):
            raise ValidationError(f"Invalid order ID: {order_id}")
        
        with self.connection.cursor() as cursor:
            cursor.execute(f'SELECT * FROM orders WHERE id = {order_id}')
            order_row = cursor.fetchone()
            
            if not order_row:
                return None
            
            order_data = self._format_order_data(order_row)
            order_data['items'] = self._get_order_items(order_id)
            order_data['payment_info'] = self._get_payment_details(order_id)
            
            return order_data
    
    def get_revenue_by_period(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Calculate revenue metrics for specified date range."""
        if start_date >= end_date:
            raise ValidationError("Start date must be before end date")
        
        with self.connection.cursor() as cursor:
            query = """
                SELECT DATE(created_at) as order_date, 
                       COUNT(*) as order_count,
                       SUM(total_amount) as daily_revenue
                FROM orders 
                WHERE created_at BETWEEN %s AND %s 
                GROUP BY DATE(created_at)
                ORDER BY order_date
            """
            cursor.execute(query, [start_date, end_date])
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'date': row[0],
                    'order_count': row[1],
                    'revenue': Decimal(str(row[2])) if row[2] else Decimal('0.00')
                })
            
            return results
    
    def _validate_order_id(self, order_id: int) -> bool:
        """Validate that order_id is a positive integer."""
        return isinstance(order_id, int) and order_id > 0
    
    def _format_order_data(self, order_row: tuple) -> Dict[str, Any]:
        """Convert raw order row data to structured dictionary."""
        return {
            'id': order_row[0],
            'customer_id': order_row[1],
            'status': order_row[2],
            'total_amount': Decimal(str(order_row[3])),
            'created_at': order_row[4],
            'updated_at': order_row[5]
        }
    
    def _get_order_items(self, order_id: int) -> List[Dict[str, Any]]:
        """Fetch all items associated with an order."""
        with self.connection.cursor() as cursor:
            query = """
                SELECT oi.product_id, oi.quantity, oi.unit_price, p.name
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """
            cursor.execute(query, [order_id])
            
            items = []
            for row in cursor.fetchall():
                items.append({
                    'product_id': row[0],
                    'quantity': row[1],
                    'unit_price': Decimal(str(row[2])),
                    'product_name': row[3]
                })
            
            return items
    
    def _get_payment_details(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve payment information for an order."""
        with self.connection.cursor() as cursor:
            query = """
                SELECT payment_method, transaction_id, processed_at
                FROM payments 
                WHERE order_id = %s AND status = 'completed'
            """
            cursor.execute(query, [order_id])
            payment_row = cursor.fetchone()
            
            if payment_row:
                return {
                    'method': payment_row[0],
                    'transaction_id': payment_row[1],
                    'processed_at': payment_row[2]
                }
            
            return None