from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PointsCalculationService:
    """Service for calculating and awarding loyalty points based on payment amounts."""
    
    DEFAULT_POINT_RATE = Decimal('0.01')
    MIN_PURCHASE_AMOUNT = Decimal('1.00')
    MAX_POINTS_PER_TRANSACTION = 10000
    
    def __init__(self, point_rate: Optional[Decimal] = None):
        self.point_rate = point_rate or self.DEFAULT_POINT_RATE
        
    def calculate_points_for_order(self, order_data: Dict[str, Any]) -> int:
        """Calculate loyalty points for a completed order."""
        try:
            total_amount = Decimal(str(order_data.get('total_amount', 0)))
            discount_amount = Decimal(str(order_data.get('discount_amount', 0)))
            
            if not self._is_eligible_for_points(total_amount, order_data):
                return 0
                
            points = self._calculate_base_points(total_amount, discount_amount)
            points = self._apply_bonus_multipliers(points, order_data)
            
            return min(points, self.MAX_POINTS_PER_TRANSACTION)
            
        except (ValueError, TypeError) as e:
            logger.error(f"Error calculating points for order: {e}")
            return 0
    
    def process_points_award(self, user_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the complete points award workflow for an order."""
        points_earned = self.calculate_points_for_order(order_data)
        
        if points_earned <= 0:
            return {
                'success': True,
                'points_awarded': 0,
                'message': 'Order not eligible for points'
            }
        
        try:
            with transaction.atomic():
                self._award_points_to_user(user_id, points_earned)
                self._log_points_transaction(user_id, order_data, points_earned)
                
            return {
                'success': True,
                'points_awarded': points_earned,
                'message': f'Successfully awarded {points_earned} points'
            }
            
        except Exception as e:
            logger.error(f"Failed to award points to user {user_id}: {e}")
            return {
                'success': False,
                'points_awarded': 0,
                'message': 'Failed to process points award'
            }
    
    def _is_eligible_for_points(self, total_amount: Decimal, order_data: Dict[str, Any]) -> bool:
        """Check if an order is eligible for points calculation."""
        if total_amount < self.MIN_PURCHASE_AMOUNT:
            return False
            
        payment_method = order_data.get('payment_method', '')
        if payment_method in ['gift_card', 'store_credit']:
            return False
            
        order_status = order_data.get('status', '')
        if order_status not in ['completed', 'shipped']:
            return False
            
        return True
    
    def _calculate_base_points(self, total_amount: Decimal, discount_amount: Decimal) -> int:
        """Calculate base points from order total."""
        if total_amount <= 0:
            return 0
            
        points = int(total_amount * self.point_rate)
        return max(0, points)
    
    def _apply_bonus_multipliers(self, base_points: int, order_data: Dict[str, Any]) -> int:
        """Apply any bonus multipliers to the base points."""
        multiplier = Decimal('1.0')
        
        if order_data.get('is_premium_member', False):
            multiplier += Decimal('0.5')
            
        if order_data.get('is_first_purchase', False):
            multiplier += Decimal('1.0')
            
        category = order_data.get('primary_category', '')
        if category in ['electronics', 'books']:
            multiplier += Decimal('0.25')
            
        return int(base_points * multiplier)
    
    def _award_points_to_user(self, user_id: int, points: int) -> None:
        """Award points to user account."""
        from django.contrib.auth import get_user_model
        from .models import UserPoints
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        user_points, created = UserPoints.objects.get_or_create(user=user)
        user_points.total_points += points
        user_points.save()
    
    def _log_points_transaction(self, user_id: int, order_data: Dict[str, Any], points: int) -> None:
        """Log the points transaction for audit purposes."""
        from .models import PointsTransaction
        
        PointsTransaction.objects.create(
            user_id=user_id,
            order_id=order_data.get('order_id'),
            points_awarded=points,
            transaction_type='order_purchase',
            order_total=order_data.get('total_amount', 0),
            discount_applied=order_data.get('discount_amount', 0)
        )