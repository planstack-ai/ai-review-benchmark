from decimal import Decimal
from typing import Optional, Dict, Any
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from myapp.models import UserPoints, PointsTransaction


class PointsService:
    """Service class for managing user points and transactions."""
    
    def __init__(self):
        self.minimum_points = Decimal('0.00')
        self.maximum_transaction = Decimal('10000.00')
    
    def get_user_points(self, user_id: int) -> Dict[str, Any]:
        """Retrieve current points balance for a user."""
        try:
            user = User.objects.get(pk=user_id)
            points_record = self._get_or_create_points_record(user)
            
            return {
                'user_id': user_id,
                'username': user.username,
                'current_balance': points_record.balance,
                'total_earned': points_record.total_earned,
                'total_spent': points_record.total_spent,
                'last_updated': points_record.updated_at
            }
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} does not exist")
    
    def add_points(self, user_id: int, amount: Decimal, description: str = "") -> bool:
        """Add points to a user's account."""
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        
        if amount > self.maximum_transaction:
            raise ValidationError(f"Amount exceeds maximum transaction limit of {self.maximum_transaction}")
        
        try:
            with transaction.atomic():
                user = User.objects.get(pk=user_id)
                points_record = self._get_or_create_points_record(user)
                
                points_record.balance += amount
                points_record.total_earned += amount
                points_record.updated_at = timezone.now()
                points_record.save()
                
                self._create_transaction_record(
                    user=user,
                    amount=amount,
                    transaction_type='CREDIT',
                    description=description or f"Points added: {amount}"
                )
                
                return True
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} does not exist")
    
    def deduct_points(self, user_id: int, amount: Decimal, description: str = "") -> bool:
        """Deduct points from a user's account."""
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        
        try:
            with transaction.atomic():
                user = User.objects.get(pk=user_id)
                points_record = self._get_or_create_points_record(user)
                
                if points_record.balance < amount:
                    raise ValidationError("Insufficient points balance")
                
                points_record.balance -= amount
                points_record.total_spent += amount
                points_record.updated_at = timezone.now()
                points_record.save()
                
                self._create_transaction_record(
                    user=user,
                    amount=amount,
                    transaction_type='DEBIT',
                    description=description or f"Points deducted: {amount}"
                )
                
                return True
        except User.DoesNotExist:
            raise ValidationError(f"User with ID {user_id} does not exist")
    
    def _get_or_create_points_record(self, user: User) -> UserPoints:
        """Get or create a points record for the user."""
        points_record, created = UserPoints.objects.get_or_create(
            user=user,
            defaults={
                'balance': Decimal('0.00'),
                'total_earned': Decimal('0.00'),
                'total_spent': Decimal('0.00')
            }
        )
        return points_record
    
    def _create_transaction_record(self, user: User, amount: Decimal, 
                                 transaction_type: str, description: str) -> None:
        """Create a transaction record for audit purposes."""
        PointsTransaction.objects.create(
            user=user,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            timestamp=timezone.now()
        )